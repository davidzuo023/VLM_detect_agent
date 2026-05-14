"""
main.py
命令行入口。
用法：python main.py --image <图片路径> --question <问题> [--format markdown]
"""

import argparse
import sys
import os

from src.utils.llm import check_config
from src.utils.image import file_to_base64
from src.agents.vlm_agent import run


def main():
    parser = argparse.ArgumentParser(
        description="Qwen VLM Agent — 多模态视觉语言 Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python main.py --image examples/sample.jpg --question "这张图里有什么？"
  python main.py --image chart.png --question "分析这个图表的趋势" --format markdown
  python main.py --image receipt.jpg --question "计算总金额" --format json
        """
    )
    parser.add_argument("--image",    "-i", required=True,  help="图片文件路径")
    parser.add_argument("--question", "-q", required=True,  help="对图片的问题")
    parser.add_argument("--format",   "-f", default="markdown",
                        choices=["text", "markdown", "json"],
                        help="输出格式（默认 markdown）")

    args = parser.parse_args()

    # 检查配置
    if not check_config():
        sys.exit(1)

    # 检查图片文件
    if not os.path.exists(args.image):
        print(f"❌ 图片文件不存在：{args.image}")
        sys.exit(1)

    print(f"\n{'='*55}")
    print(f"  🤖 Qwen VLM Agent")
    print(f"{'='*55}")
    print(f"  📸 图片：{args.image}")
    print(f"  ❓ 问题：{args.question}")
    print(f"  📄 格式：{args.format}")
    print(f"{'='*55}\n")

    # 转换图片
    try:
        image_b64, media_type = file_to_base64(args.image)
    except Exception as e:
        print(f"❌ 图片读取失败：{e}")
        sys.exit(1)

    # 运行 Agent
    result = run(
        image_base64=image_b64,
        image_media_type=media_type,
        user_question=args.question,
        output_format=args.format,
    )

    # 输出结果
    print(f"\n{'='*55}")
    print(f"  🤖 最终回答")
    print(f"{'='*55}\n")
    print(result.get("final_answer", "未能生成回答"))
    print(f"\n{'='*55}")


if __name__ == "__main__":
    main()
