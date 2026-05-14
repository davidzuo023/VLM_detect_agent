"""
tests/test_tools.py
工具单元测试（不需要 API Key 即可运行）。
运行：pytest tests/test_tools.py -v
"""

import pytest
from src.tools.calculator import calculate
from src.tools.search import web_search
from src.tools.weather import get_weather


class TestCalculator:

    def test_basic_addition(self):
        result = calculate("1 + 2")
        assert "3" in result

    def test_multiplication(self):
        result = calculate("6 * 7")
        assert "42" in result

    def test_sqrt(self):
        result = calculate("sqrt(144)")
        assert "12" in result

    def test_pi_constant(self):
        result = calculate("pi")
        assert "3.14" in result

    def test_power(self):
        result = calculate("2^10")
        assert "1024" in result

    def test_complex_expression(self):
        result = calculate("sqrt(16) + 2 * 3")
        assert "10" in result

    def test_division_by_zero(self):
        result = calculate("1 / 0")
        assert "零" in result or "zero" in result.lower()

    def test_unsafe_expression(self):
        result = calculate("__import__('os').system('ls')")
        assert "不安全" in result or "失败" in result


class TestSearchWithoutKey:

    def test_no_api_key_graceful(self):
        """没有 API Key 时应该返回提示而不是崩溃。"""
        import os
        original = os.environ.get("TAVILY_API_KEY", "")
        os.environ["TAVILY_API_KEY"] = ""
        try:
            result = web_search("test query")
            assert "未配置" in result or "TAVILY" in result
        finally:
            os.environ["TAVILY_API_KEY"] = original


class TestWeatherWithoutKey:

    def test_no_api_key_graceful(self):
        """没有 API Key 时应该返回提示而不是崩溃。"""
        import os
        original = os.environ.get("WEATHER_API_KEY", "")
        os.environ["WEATHER_API_KEY"] = ""
        try:
            result = get_weather("Beijing")
            assert "未配置" in result or "WEATHER" in result
        finally:
            os.environ["WEATHER_API_KEY"] = original
