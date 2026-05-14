"""
src/utils/llm.py
统一的 LLM 初始化模块。
所有节点从这里获取 vlm / llm 实例，便于统一管理和切换模型。
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# ── 从环境变量读取配置 ──
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = os.getenv(
    "DASHSCOPE_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1"
)
VLM_MODEL = os.getenv("VLM_MODEL", "qwen-vl-plus")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3.6-plus")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


def get_vlm() -> ChatOpenAI:
    """
    获取视觉语言模型（VLM）实例。
    用于图像分析节点，支持图片 + 文字多模态输入。

    默认模型：qwen-vl-plus（有免费额度）
    强力模型：qwen-vl-max（效果更好）
    推理模型：qvq-72b-preview（带思维链）
    """
    return ChatOpenAI(
        model=VLM_MODEL,
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
        temperature=0.1,          # 视觉分析追求准确，温度低
        max_tokens=2048,
    )


def get_llm() -> ChatOpenAI:
    """
    获取纯文本推理模型实例。
    用于路由判断、工具参数生成、最终答案综合等节点。

    默认模型：qwen3.6-plus（能力强，响应快）
    """
    return ChatOpenAI(
        model=LLM_MODEL,
        api_key=DASHSCOPE_API_KEY,
        base_url=DASHSCOPE_BASE_URL,
        temperature=0.3,
        max_tokens=2048,
    )


def check_config() -> bool:
    """启动时检查必要配置是否齐全。"""
    if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "sk-your-key-here":
        print("❌ 错误：未配置 DASHSCOPE_API_KEY")
        print("   请在 .env 文件中填入你的阿里云百炼 API Key")
        print("   获取地址：https://bailian.console.aliyun.com")
        return False
    if DEBUG:
        print(f"✅ LLM 配置：{LLM_MODEL} @ {DASHSCOPE_BASE_URL}")
        print(f"✅ VLM 配置：{VLM_MODEL}")
    return True
