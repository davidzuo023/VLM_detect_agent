"""
src/nodes/router.py
Node 2 — route_decision
智能路由节点：分析图片描述 + 用户问题，决定走哪条路径。

路由结果：
  - needs_tool=False → 直接回答（direct_answer）
  - needs_tool=True  → 工具调用（tool_call → synthesize）
"""

from langchain_core.messages import HumanMessage

from src.utils.llm import get_llm
from src.utils.state import AgentState

ROUTER_PROMPT = """你是一个智能任务路由器。根据图片内容和用户问题，判断是否需要调用外部工具。

图片分析摘要：
{description}

用户问题：{question}

需要调用工具的情况（回答 TOOL）：
- 需要搜索最新信息（价格、新闻、实时数据）
- 需要精确数学计算（复杂公式、统计计算）
- 需要查询天气信息
- 图片中有需要查询的商品/地点/人物

可以直接回答的情况（回答 DIRECT）：
- 图片描述 + 通用知识已足够回答
- 纯图片内容理解（描述、OCR、场景分析）
- 解释图表含义（不需要额外数据）

同时，如果需要工具，请指定：
- 工具名称：search / calculator / weather
- 工具查询参数：具体的查询语句

请严格按以下 JSON 格式回答，不要有其他文字：
{{
  "decision": "DIRECT" 或 "TOOL",
  "tool_name": "search" 或 "calculator" 或 "weather" 或 null,
  "tool_query": "工具查询内容" 或 null,
  "reason": "简短说明路由理由"
}}"""


def route_decision_node(state: AgentState) -> dict:
    """
    Node: route_decision

    输入：image_description, user_question
    输出：needs_tool, tool_name, tool_query（写入 state）
    """
    print("🤔 [Node 2/4] route_decision — 判断路由...")

    llm = get_llm()
    description = state.get("image_description", "")
    question = state.get("user_question", "")

    prompt = ROUTER_PROMPT.format(
        description=description[:800],  # 避免 prompt 过长
        question=question,
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip()

    # 解析 JSON 路由结果
    import json, re
    try:
        # 提取 JSON 部分（防止模型输出额外文字）
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"decision": "DIRECT", "tool_name": None, "tool_query": None}
    except (json.JSONDecodeError, Exception):
        result = {"decision": "DIRECT", "tool_name": None, "tool_query": None}

    needs_tool = result.get("decision", "DIRECT").upper() == "TOOL"
    tool_name = result.get("tool_name")
    tool_query = result.get("tool_query")
    reason = result.get("reason", "")

    print(f"   ✅ 路由结果：{'🔧 工具调用' if needs_tool else '💬 直接回答'}"
          f"{'（' + tool_name + '）' if tool_name else ''} — {reason}")

    return {
        "needs_tool": needs_tool,
        "tool_name": tool_name,
        "tool_query": tool_query,
    }


def router_conditional(state: AgentState) -> str:
    """
    LangGraph 条件边函数。
    根据 route_decision_node 的结果，返回下一个节点名称。
    """
    if state.get("needs_tool", False):
        return "tool_call"
    return "direct_answer"
