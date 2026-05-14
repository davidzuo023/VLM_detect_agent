"""
src/nodes/answer.py
Node 3a — direct_answer
当路由判断不需要工具时，直接基于图片分析结果和通用知识生成回答。
"""

from langchain_core.messages import HumanMessage, SystemMessage

from src.utils.llm import get_llm
from src.utils.state import AgentState


SYSTEM_PROMPT = """你是一个专业的多模态 AI 助手，擅长图片理解和分析。
基于图片内容和你的知识，给出准确、详细、有帮助的回答。
回答要结构清晰，重点突出。"""

ANSWER_PROMPT = """根据以下图片分析结果，请回答用户的问题。

【图片内容分析】
{description}

【用户问题】
{question}

【输出格式要求】
{format_instruction}

请用中文回答："""

FORMAT_INSTRUCTIONS = {
    "text":     "用自然流畅的文字回答，段落清晰。",
    "markdown": "用 Markdown 格式回答，合理使用标题、列表、加粗等。",
    "json":     "用 JSON 格式输出，结构化组织关键信息。",
}


def direct_answer_node(state: AgentState) -> dict:
    """
    Node: direct_answer

    输入：image_description, user_question, output_format
    输出：final_answer（写入 state），messages（追加）
    """
    print("💬 [Node 3a/4] direct_answer — 生成直接回答...")

    llm = get_llm()
    description = state.get("image_description", "")
    question = state.get("user_question", "")
    output_format = state.get("output_format", "markdown")

    format_instruction = FORMAT_INSTRUCTIONS.get(output_format, FORMAT_INSTRUCTIONS["markdown"])

    prompt = ANSWER_PROMPT.format(
        description=description,
        question=question,
        format_instruction=format_instruction,
    )

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    answer = response.content
    print(f"   ✅ 回答生成完成（{len(answer)} 字）")

    return {
        "final_answer": answer,
        "messages": [response],
    }
