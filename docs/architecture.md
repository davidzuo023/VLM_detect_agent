# 架构说明文档

## 整体设计思路

Qwen VLM Agent 的设计遵循**关注点分离**原则：
- `nodes/` 只负责单一功能，互相独立
- `agents/` 负责编排节点之间的流程
- `tools/` 是独立的工具函数，可单独测试
- `utils/` 提供共享基础设施

## LangGraph 状态流转

```
AgentState 初始化
{
  user_question: "..."
  image_base64: "..."
  image_description: ""     ← 等待 analyze_image 填入
  needs_tool: False         ← 等待 route_decision 填入
  tool_result: None         ← 等待 tool_call 填入
  final_answer: ""          ← 等待 answer/synthesize 填入
}

[analyze_image]
  读取: image_base64, user_question
  写入: image_description

[route_decision]
  读取: image_description, user_question
  写入: needs_tool, tool_name, tool_query

[direct_answer] (needs_tool=False)
  读取: image_description, user_question
  写入: final_answer
  → END

[tool_call] (needs_tool=True)
  读取: tool_name, tool_query
  写入: tool_result
  → [synthesize_answer]

[synthesize_answer]
  读取: image_description, tool_result, user_question
  写入: final_answer
  → END
```

## 扩展指南

### 添加新工具
1. 在 `src/tools/` 新建 `my_tool.py`
2. 实现 `def my_tool(query: str) -> str` 函数
3. 在 `src/nodes/synthesize.py` 的 `TOOL_REGISTRY` 中注册
4. 在 `src/nodes/router.py` 的 `ROUTER_PROMPT` 中说明使用场景

### 添加新节点
1. 在 `src/nodes/` 新建节点文件
2. 在 `src/agents/vlm_agent.py` 中 `graph.add_node()` 注册
3. 用 `graph.add_edge()` 或 `graph.add_conditional_edges()` 连接

### 切换模型
修改 `.env` 中的变量即可，无需改代码：
```
VLM_MODEL=qwen-vl-max         # 切换视觉模型
LLM_MODEL=qwen3.6-plus        # 切换文本模型
```
