<div align="center">

# 🤖 Qwen VLM Agent

**基于 LangGraph + Qwen3.6-Plus 构建的多模态视觉语言 Agent**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-green)](https://github.com/langchain-ai/langgraph)
[![Qwen](https://img.shields.io/badge/Model-Qwen3.6--Plus-orange)](https://help.aliyun.com/zh/model-studio/models)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Stars](https://img.shields.io/github/stars/davidzuo023/qwen-vlm-agent?style=social)](https://github.com/yourname/qwen-vlm-agent)


</div>

---

## ✨ 项目简介

**Qwen VLM Agent** 是一个基于 **LangGraph** 状态机 + **阿里云百炼 Qwen3.6-Plus** 大模型构建的开源多模态 Agent 框架。

它不只是一个简单的图片问答工具——它是一个**完整的 Agent 系统**，具备：

- 🧠 **视觉理解**：调用 Qwen-VL 分析图片内容（OCR、图表、场景、人物）
- 🔀 **智能路由**：LangGraph 根据任务类型自动选择工具或直接回答
- 🔧 **工具调用**：网络搜索、数学计算、天气查询等工具无缝集成
- 💬 **多轮记忆**：跨对话保留上下文，支持追问和延续分析
- 📊 **结构化输出**：支持 JSON、Markdown、表格等多种输出格式
- 🌐 **Web UI**：内置 Gradio 可视化界面，开箱即用

---

## 🎯 功能演示

| 场景 | 输入 | Agent 行为 |
|------|------|-----------|
| 图表分析 | 折线图 + "分析趋势" | VLM 提取数据 → 推理分析 → 结构化输出 |
| 文档 OCR | 截图 + "提取文字" | VLM OCR → 格式化文本 |
| 商品识别 | 商品照片 + "搜索价格" | VLM 识别 → 工具搜索 → 汇总报价 |
| 数学题 | 习题图片 + "解题" | VLM 读题 → 推理计算 → 步骤输出 |
| 场景问答 | 任意图片 + 任意问题 | 动态路由 → 最优路径回答 |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourname/qwen-vlm-agent.git
cd qwen-vlm-agent
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

`.env` 填写示例：
```
DASHSCOPE_API_KEY=sk-xxxxxxxx   # 阿里云百炼 API Key
TAVILY_API_KEY=tvly-xxxxxxxx    # 可选，Tavily 搜索工具
```

> 获取百炼 API Key：[bailian.console.aliyun.com](https://bailian.console.aliyun.com)（新用户90天免费额度）

### 4. 运行

```bash
# 命令行模式
python main.py --image examples/sample.jpg --question "这张图里有什么？"

# Web UI 模式
python app.py
# 打开 http://localhost:7860
```

---

## 🗂 项目结构

```
qwen-vlm-agent/
├── main.py                  # 命令行入口
├── app.py                   # Gradio Web UI
├── requirements.txt
├── .env.example
│
├── src/
│   ├── agents/
│   │   └── vlm_agent.py     # LangGraph Agent 主逻辑（图构建）
│   ├── nodes/
│   │   ├── analyze.py       # Node: VLM 图像分析
│   │   ├── router.py        # Node: 智能路由判断
│   │   ├── answer.py        # Node: 直接回答生成
│   │   └── synthesize.py    # Node: 工具结果综合
│   ├── tools/
│   │   ├── search.py        # 工具: 网络搜索（Tavily）
│   │   ├── calculator.py    # 工具: 数学计算
│   │   └── weather.py       # 工具: 天气查询
│   └── utils/
│       ├── image.py         # 图片处理工具函数
│       ├── state.py         # LangGraph State 定义
│       └── llm.py           # LLM 初始化配置
│
├── tests/
│   ├── test_agent.py
│   └── test_tools.py
├── docs/
│   └── architecture.md      # 架构说明文档
├── examples/
│   └── sample.jpg           # 示例图片
└── .github/
    └── workflows/
        └── ci.yml           # GitHub Actions CI
```

---

## 🧩 架构设计

```
用户输入（图片 + 问题）
        ↓
  ┌─────────────────────────────────────┐
  │         LangGraph StateGraph        │
  │                                     │
  │  [analyze_image]                    │
  │    Qwen-VL 视觉理解 → 图片描述      │
  │         ↓                           │
  │  [route_decision]  ◄── 条件路由     │
  │    判断：需要工具 or 直接回答？      │
  │       /         \                   │
  │  [tool_call]  [direct_answer]       │
  │  搜索/计算     直接生成回答         │
  │       \         /                   │
  │  [synthesize_answer]                │
  │    综合所有信息，生成最终回答        │
  └─────────────────────────────────────┘
        ↓
   返回结构化回答
```

---

## 🔧 配置说明

在 `src/utils/llm.py` 中可切换模型：

| 模型 | 说明 | 适合场景 |
|------|------|---------|
| `qwen-vl-plus` | 视觉理解，免费额度 | 开发测试 |
| `qwen-vl-max` | 最强视觉能力 | 生产环境 |
| `qvq-72b-preview` | 视觉推理+思维链 | 复杂分析 |
| `qwen3-vl-flash` | 轻量快速 | 高并发场景 |

---

## 🤝 贡献指南

欢迎 PR 和 Issue！

1. Fork 本仓库
2. 创建分支：`git checkout -b feature/your-feature`
3. 提交代码：`git commit -m 'feat: add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 发起 Pull Request

---

## 📄 License

MIT License © 2026 [davidzuo023](https://github.com/yourname)

---

<div align="center">
如果这个项目对你有帮助，请给一个 ⭐ Star！
</div>
