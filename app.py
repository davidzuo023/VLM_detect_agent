"""
app.py
Gradio Web UI 入口。
运行：python app.py
访问：http://localhost:7860
"""

import os
import sys
import gradio as gr
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

from src.utils.llm import check_config
from src.utils.image import pil_to_base64, resize_if_needed
from src.agents.vlm_agent import run

# ─────────────────────────────────────────
# 核心处理函数
# ─────────────────────────────────────────

def process(image: Image.Image, question: str, output_format: str, history: list):
    """Gradio 事件处理函数：调用 Agent 并更新聊天历史。"""
    if image is None:
        history.append({"role": "assistant", "content": "⚠️ 请先上传一张图片。"})
        return history, history

    if not question.strip():
        history.append({"role": "assistant", "content": "⚠️ 请输入你的问题。"})
        return history, history

    history.append({"role": "user", "content": f"📸 {question}"})
    yield history, history

    try:
        # 图片预处理
        img = resize_if_needed(image, max_size=2048)
        image_b64, media_type = pil_to_base64(img)

        # 运行 Agent
        result = run(
            image_base64=image_b64,
            image_media_type=media_type,
            user_question=question,
            output_format=output_format,
        )

        answer = result.get("final_answer", "未能生成回答")
        desc = result.get("image_description", "")
        used_tool = result.get("tool_name")

        # 构建展示内容
        parts = []
        if desc:
            preview = desc[:200] + ("…" if len(desc) > 200 else "")
            parts.append(f"**🔍 图片理解**\n{preview}")
        if used_tool:
            parts.append(f"**🔧 调用工具**：`{used_tool}`")
        parts.append(f"**💬 回答**\n\n{answer}")

        full_response = "\n\n---\n\n".join(parts)

    except Exception as e:
        full_response = f"❌ 运行出错：{str(e)}\n\n请检查 `.env` 中的 API Key 配置。"

    history.append({"role": "assistant", "content": full_response})
    yield history, history


def clear_all():
    return [], [], None, ""


# ─────────────────────────────────────────
# Gradio UI 构建
# ─────────────────────────────────────────

CSS = """
.container { max-width: 1000px; margin: auto; }
.header-title { font-size: 2rem; font-weight: 700; text-align: center; margin-bottom: 4px; }
.header-sub { text-align: center; color: #888; margin-bottom: 24px; font-size: 0.95rem; }
footer { display: none !important; }
"""

# 改后
with gr.Blocks(title="Qwen VLM Agent") as demo:

    state = gr.State([])

    with gr.Column(elem_classes="container"):
        gr.HTML("""
        <div class="header-title">🤖 Qwen VLM Agent</div>
        <div class="header-sub">
            LangGraph × Qwen3.6-Plus × 阿里云百炼 · 多模态视觉语言 Agent
        </div>
        """)

        with gr.Row():
            # ── 左侧：输入区 ──
            with gr.Column(scale=1):
                image_input = gr.Image(
                    label="📸 上传图片",
                    type="pil",
                    height=300,
                    sources=["upload", "clipboard"],
                )

                question_input = gr.Textbox(
                    label="❓ 你的问题",
                    placeholder="输入对这张图片的问题...",
                    lines=3,
                )

                output_format = gr.Radio(
                    choices=["markdown", "text", "json"],
                    value="markdown",
                    label="📄 输出格式",
                )

                with gr.Row():
                    submit_btn = gr.Button("发送 ↗", variant="primary", scale=3)
                    clear_btn  = gr.Button("清空",                       scale=1)

                gr.Examples(
                    label="💡 示例问题",
                    examples=[
                        ["这张图里有什么内容？请详细描述。"],
                        ["提取图片中所有文字信息（OCR）"],
                        ["分析图表数据，描述趋势和关键数据点"],
                        ["识别这个商品，并搜索参考价格"],
                        ["解答图片中的数学题，给出步骤"],
                        ["这张图片的场景在哪里？"],
                    ],
                    inputs=[question_input],
                )

            # ── 右侧：对话区 ──
            with gr.Column(scale=2):
                # 改后
                chatbot = gr.Chatbot(
                    label="💬 对话历史",
                    height=520,
                    render_markdown=True,
                )

        # ── 架构说明 ──
        with gr.Accordion("📊 Agent 工作流程", open=False):
            gr.Markdown("""
            ```
            用户输入（图片 + 问题）
                    ↓
            [analyze_image]   ← Qwen-VL 多模态视觉分析（提取图片全部信息）
                    ↓
            [route_decision]  ← Qwen3.6-Plus 智能路由判断
                   / \\
                  /   \\
            [tool_call]   [direct_answer]
            搜索/计算/天气    直接生成回答
                  \\   /
                   \\ /
            [synthesize_answer] ← 综合图片分析 + 工具结果，输出最终回答
            ```
            **支持工具**：🔍 Tavily 网络搜索 · 🧮 数学计算器 · 🌤️ 天气查询
            """)

        with gr.Accordion("⚙️ 配置与模型说明", open=False):
            gr.Markdown("""
            **必须配置（`.env`）**
            ```
            DASHSCOPE_API_KEY=sk-xxxxxxxx
            ```
            获取地址：[bailian.console.aliyun.com](https://bailian.console.aliyun.com)（新用户 90 天免费额度）

            **可选工具配置**
            ```
            TAVILY_API_KEY=tvly-xxx       # 网络搜索
            WEATHER_API_KEY=xxx           # 天气查询
            ```

            **VLM 模型选项（修改 `.env` 中的 VLM_MODEL）**
            | 模型 | 特点 |
            |------|------|
            | `qwen-vl-plus` | 通用视觉，有免费额度，推荐开发测试 |
            | `qwen-vl-max` | 最强视觉能力，适合生产环境 |
            | `qvq-72b-preview` | 视觉推理 + 思维链 |
            | `qwen3-vl-flash` | 轻量快速，低成本高并发 |
            """)

    # ── 事件绑定 ──
    submit_btn.click(
        fn=process,
        inputs=[image_input, question_input, output_format, state],
        outputs=[chatbot, state],
    )
    question_input.submit(
        fn=process,
        inputs=[image_input, question_input, output_format, state],
        outputs=[chatbot, state],
    )
    clear_btn.click(
        fn=clear_all,
        outputs=[chatbot, state, image_input, question_input],
    )


if __name__ == "__main__":
    if not check_config():
        sys.exit(1)

    port = int(os.getenv("GRADIO_PORT", "7860"))
    print(f"\n🚀 Qwen VLM Agent 启动中...")
    print(f"   访问地址：http://localhost:{port}\n")

    # 改后
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        inbrowser=True,
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"),
    )
