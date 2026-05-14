"""
src/utils/state.py
LangGraph Agent 的核心状态定义。
整个 Agent 运行期间，所有节点共享并修改这个 State。
"""

from typing import TypedDict, Annotated, Optional
import operator
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    LangGraph 全局状态。
    每个节点读取需要的字段，写入自己的输出字段。
    Annotated[list, operator.add] 表示 messages 字段是追加合并的。
    """

    # ── 对话历史（追加模式）──
    messages: Annotated[list[BaseMessage], operator.add]

    # ── 用户输入 ──
    user_question: str                    # 用户提问
    image_base64: str                     # 图片的 base64 编码
    image_media_type: str                 # 图片 MIME 类型，如 image/jpeg

    # ── 中间结果 ──
    image_description: str               # VLM 对图片的详细分析结果
    needs_tool: bool                     # 路由判断：是否需要工具
    tool_name: Optional[str]             # 决定调用的工具名称
    tool_query: Optional[str]            # 工具调用的查询参数
    tool_result: Optional[str]           # 工具返回的结果

    # ── 最终输出 ──
    final_answer: str                    # Agent 最终回答
    output_format: str                   # 输出格式：text / markdown / json
