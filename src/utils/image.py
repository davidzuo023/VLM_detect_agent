"""
src/utils/image.py
图片处理工具函数集合。
负责图片读取、格式转换、base64 编码等操作。
"""

import base64
import os
from io import BytesIO
from pathlib import Path

from PIL import Image


# 支持的图片格式
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

# MIME 类型映射
MIME_MAP = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".webp": "image/webp",
    ".bmp":  "image/bmp",
}


def file_to_base64(image_path: str) -> tuple[str, str]:
    """
    将图片文件转换为 base64 字符串。

    Returns:
        (base64_string, media_type)
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"图片文件不存在：{image_path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise ValueError(f"不支持的图片格式：{suffix}，支持：{SUPPORTED_FORMATS}")

    media_type = MIME_MAP.get(suffix, "image/jpeg")

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return b64, media_type


def pil_to_base64(pil_image: Image.Image, format: str = "JPEG") -> tuple[str, str]:
    """
    将 PIL Image 对象转换为 base64 字符串。
    Gradio 上传的图片会以 PIL 格式传入。

    Returns:
        (base64_string, media_type)
    """
    # RGBA 转 RGB（JPEG 不支持透明通道）
    if pil_image.mode in ("RGBA", "P") and format == "JPEG":
        pil_image = pil_image.convert("RGB")

    buffer = BytesIO()
    pil_image.save(buffer, format=format)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    media_type = f"image/{format.lower()}"

    return b64, media_type


def build_image_message_content(
    base64_str: str,
    media_type: str,
    text: str,
    detail: str = "high",
) -> list[dict]:
    """
    构建符合 OpenAI 多模态格式的消息 content。
    detail: "high"（高精度）/ "low"（低精度，省 Token）/ "auto"
    """
    return [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:{media_type};base64,{base64_str}",
                "detail": detail,
            },
        },
        {
            "type": "text",
            "text": text,
        },
    ]


def resize_if_needed(pil_image: Image.Image, max_size: int = 2048) -> Image.Image:
    """
    如果图片太大，等比例缩放到 max_size 以内。
    避免消耗过多 Token。
    """
    w, h = pil_image.size
    if max(w, h) <= max_size:
        return pil_image

    if w > h:
        new_w, new_h = max_size, int(h * max_size / w)
    else:
        new_w, new_h = int(w * max_size / h), max_size

    return pil_image.resize((new_w, new_h), Image.LANCZOS)
