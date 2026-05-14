"""
src/agents/vlm_agent.py
LangGraph Agent 核心 —— 图的构建与编译。

这里定义了整个 Agent 的拓扑结构：
  - 节点（Nodes）：每个处理步骤
  - 边（Edges）：节点之间的数据流
  - 条件边（Conditional Edges）：动态路由

图结构：
  START
    → analyze_image       （VLM 视觉分析）
    → route_decision      （智能路由）
    → [direct_answer]     （无需工具时直接回答）
    → [tool_call]         （调用搜索/计算/天气工具）
      → synthesize_answer （综合工具结果生成回答）
  END
"""

from langgraph.graph import StateGraph, END

from src.utils.state import AgentState
from src.nodes.analyze import analyze_image_node
from src.nodes.router import route_decision_node, router_conditional
from src.nodes.answer import direct_answer_node
from src.nodes.synthesize import tool_call_node, synthesize_answer_node


def build_agent():
    """
    构建并编译 LangGraph Agent。

    Returns:
        compiled LangGraph app，可直接调用 .invoke(state) 运行
    """

    # ── 初始化 StateGraph ──
    graph = StateGraph(AgentState)

    # ── 注册节点 ──
    graph.add_node("analyze_image",    analyze_image_node)
    graph.add_node("route_decision",   route_decision_node)
    graph.add_node("direct_answer",    direct_answer_node)
    graph.add_node("tool_call",        tool_call_node)
    graph.add_node("synthesize_answer", synthesize_answer_node)

    # ── 设置入口节点 ──
    graph.set_entry_point("analyze_image")

    # ── 固定边 ──
    graph.add_edge("analyze_image", "route_decision")
    graph.add_edge("direct_answer", END)
    graph.add_edge("tool_call",     "synthesize_answer")
    graph.add_edge("synthesize_answer", END)

    # ── 条件边：路由判断后分支 ──
    graph.add_conditional_edges(
        "route_decision",       # 起始节点
        router_conditional,     # 路由函数（返回节点名称字符串）
        {
            "direct_answer":    "direct_answer",    # DIRECT 路径
            "tool_call":        "tool_call",         # TOOL 路径
        }
    )

    # ── 编译图 ──
    return graph.compile()


def run(
    image_base64: str,
    image_media_type: str,
    user_question: str,
    output_format: str = "markdown",
) -> dict:
    """
    运行 Agent 的便捷函数。

    Args:
        image_base64:     图片 base64 编码
        image_media_type: 图片 MIME 类型
        user_question:    用户问题
        output_format:    输出格式 text/markdown/json

    Returns:
        完整的 AgentState dict，包含 final_answer 等所有字段
    """
    agent = build_agent()

    initial_state = AgentState(
        messages=[],
        user_question=user_question,
        image_base64=image_base64,
        image_media_type=image_media_type,
        image_description="",
        needs_tool=False,
        tool_name=None,
        tool_query=None,
        tool_result=None,
        final_answer="",
        output_format=output_format,
    )

    return agent.invoke(initial_state)
