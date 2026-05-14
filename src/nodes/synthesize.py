"""
src/nodes/synthesize.py
Node 3b — tool_call       : 根据路由结果执行对应工具
Node 4  — synthesize_answer: 将图片分析 + 工具结果合并，生成最终回答
"""

from langchain_core.messages import HumanMessage, SystemMessage

from src.utils.llm import get_llm
from src.utils.state import AgentState
from src.tools.search import web_search
from src.tools.calculator import calculate
from src.tools.weather import get_weather


# ─────────────────────────────────────────
# Node 3b: tool_call
# ─────────────────────────────────────────

TOOL_REGISTRY = {
    "search":     web_search,
    "calculator": calculate,
    "weather":    get_weather,
}


def tool_call_node(state: AgentState) -> dict:
    """
    Node: tool_call

    根据路由节点指定的工具名和查询参数，执行对应工具。
    输入：tool_name, tool_query
    输出：tool_result（写入 state）
    """
    tool_name = state.get("tool_name", "search")
    tool_query = state.get("tool_query", "")

    print(f"🔧 [Node 3b/4] tool_call — 调用工具：{tool_name}({tool_query[:50]}...)")

    tool_fn = TOOL_REGISTRY.get(tool_name, web_search)

    try:
        result = tool_fn(tool_query)
        print(f"   ✅ 工具调用成功（{len(result)} 字）")
    except Exception as e:
        result = f"工具调用失败：{str(e)}"
        print(f"   ❌ 工具调用失败：{e}")

    return {"tool_result": result}


# ─────────────────────────────────────────
# Node 4: synthesize_answer
# ─────────────────────────────────────────

SYSTEM_PROMPT = """你是一个专业的多模态 AI 助手，擅长综合多方信息给出准确答案。"""

SYNTHESIZE_PROMPT = """请综合以下所有信息，给出完整、准确的最终回答。

【图片内容分析】
{description}

【工具查询结果（{tool_name}）】
{tool_result}

【用户问题】
{question}

【输出格式要求】
{format_instruction}

请基于图片内容和工具结果，给出最终综合回答（中文，结构清晰）："""

FORMAT_INSTRUCTIONS = {
    "text":     "用自然流畅的文字回答。",
    "markdown": "用 Markdown 格式，合理使用标题、列表、加粗等。",
    "json":     "用 JSON 格式，结构化输出所有关键信息。",
}


def synthesize_answer_node(state: AgentState) -> dict:
    """
    Node: synthesize_answer

    输入：image_description, tool_result, tool_name, user_question, output_format
    输出：final_answer（写入 state），messages（追加）
    """
    print("📝 [Node 4/4] synthesize_answer — 综合生成最终回答...")

    llm = get_llm()
    description = state.get("image_description", "")
    tool_result = state.get("tool_result", "无工具结果")
    tool_name = state.get("tool_name", "unknown")
    question = state.get("user_question", "")
    output_format = state.get("output_format", "markdown")

    format_instruction = FORMAT_INSTRUCTIONS.get(output_format, FORMAT_INSTRUCTIONS["markdown"])

    prompt = SYNTHESIZE_PROMPT.format(
        description=description,
        tool_name=tool_name,
        tool_result=tool_result,
        question=question,
        format_instruction=format_instruction,
    )

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    answer = response.content
    print(f"   ✅ 综合回答生成完成（{len(answer)} 字）")

    return {
        "final_answer": answer,
        "messages": [response],
    }
