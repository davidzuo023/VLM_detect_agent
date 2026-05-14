"""
src/nodes/analyze.py
Node 1 — analyze_image
使用 Qwen-VL 对图片进行深度视觉分析。
这是整个 Agent 的"眼睛"，负责把图片转化为文字描述，供后续节点使用。
"""

from langchain_core.messages import HumanMessage

from src.utils.llm import get_vlm
from src.utils.image import build_image_message_content
from src.utils.state import AgentState


ANALYZE_PROMPT = """你是一个专业的视觉分析助手。请对这张图片进行全面深入的分析，包括：

1. **主体内容**：图片中有什么？主要元素是什么？
2. **文字信息**：图中是否含有文字、数字、公式？如有请完整提取。
3. **图表数据**：如果是图表，请提取轴标签、数据点、趋势等关键信息。
4. **场景与背景**：环境、场景、时间、地点线索。
5. **关键细节**：颜色、形状、品牌、符号等重要细节。
6. **与问题的关联**：针对用户的问题，重点分析相关内容。

用户问题：{question}

请用中文回答，层次清晰，信息完整。"""


def analyze_image_node(state: AgentState) -> dict:
    """
    Node: analyze_image

    输入：image_base64, image_media_type, user_question
    输出：image_description（写入 state），messages（追加）

    使用 Qwen-VL 多模态模型分析图片，生成详细的图片描述。
    """
    print("🔍 [Node 1/4] analyze_image — 正在分析图片...")

    vlm = get_vlm()
    question = state.get("user_question", "请描述这张图片")
    image_b64 = state["image_base64"]
    media_type = state.get("image_media_type", "image/jpeg")

    # 构建多模态消息
    content = build_image_message_content(
        base64_str=image_b64,
        media_type=media_type,
        text=ANALYZE_PROMPT.format(question=question),
        detail="high",
    )

    msg = HumanMessage(content=content)
    response = vlm.invoke([msg])
    description = response.content

    print(f"   ✅ 图片分析完成（{len(description)} 字）")

    return {
        "image_description": description,
        "messages": [response],
    }
