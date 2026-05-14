"""
src/tools/weather.py
工具：天气查询
使用 OpenWeatherMap API 查询实时天气信息。
没有 API Key 时自动降级为提示信息。
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_weather(location: str) -> str:
    """
    查询指定城市的实时天气。

    Args:
        location: 城市名称，如 "北京"、"Shanghai"、"Singapore"

    Returns:
        天气信息文本
    """
    api_key = os.getenv("WEATHER_API_KEY", "")

    if not api_key or api_key == "your-weather-key-here":
        return (
            f"【天气工具未配置】\n"
            f"查询城市：{location}\n"
            f"请在 .env 中配置 WEATHER_API_KEY。\n"
            f"免费获取：https://openweathermap.org/api"
        )

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric",
            "lang": "zh_cn",
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        city = data.get("name", location)
        country = data["sys"].get("country", "")
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]

        return (
            f"**{city}, {country} 实时天气**\n"
            f"- 天气状况：{description}\n"
            f"- 温度：{temp}°C（体感 {feels_like}°C）\n"
            f"- 湿度：{humidity}%\n"
            f"- 风速：{wind_speed} m/s"
        )

    except requests.exceptions.ConnectionError:
        return f"网络连接失败，无法查询 {location} 天气"
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"未找到城市：{location}，请检查城市名称是否正确"
        return f"天气查询失败：{str(e)}"
    except Exception as e:
        return f"天气查询出错：{str(e)}"
