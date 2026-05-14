"""
src/tools/calculator.py
工具：数学计算
安全地执行数学表达式计算，支持基础运算和常用数学函数。
"""

import math
import re


# 允许的数学函数和常量（白名单）
SAFE_NAMESPACE = {
    # 基础数学函数
    "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
    "pow": pow, "divmod": divmod,
    # math 模块常用函数
    "sqrt": math.sqrt, "log": math.log, "log2": math.log2,
    "log10": math.log10, "exp": math.exp,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "ceil": math.ceil, "floor": math.floor,
    "factorial": math.factorial,
    # 常量
    "pi": math.pi, "e": math.e, "inf": math.inf,
}


def calculate(expression: str) -> str:
    """
    安全计算数学表达式。

    Args:
        expression: 数学表达式字符串，如 "sqrt(144) + 2 * pi"

    Returns:
        计算结果字符串
    """
    # 清理表达式
    expr = expression.strip()

    # 安全检查：只允许数学字符
    allowed_pattern = r'^[\d\s\+\-\*\/\(\)\.\,\%\^a-zA-Z_]+$'
    if not re.match(allowed_pattern, expr):
        return f"表达式包含不安全字符：{expression}"

    # 替换 ^ 为 ** （支持 2^10 写法）
    expr = expr.replace("^", "**")

    try:
        result = eval(expr, {"__builtins__": {}}, SAFE_NAMESPACE)  # noqa: S307

        # 格式化输出
        if isinstance(result, float):
            if result == int(result):
                formatted = str(int(result))
            else:
                formatted = f"{result:.6g}"
        else:
            formatted = str(result)

        return f"计算结果：{expression} = **{formatted}**"

    except ZeroDivisionError:
        return "错误：除数不能为零"
    except OverflowError:
        return "错误：数值过大，超出计算范围"
    except Exception as e:
        return f"计算失败：{str(e)}\n表达式：{expression}"
