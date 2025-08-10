"""天気情報を取得するLangGraph

都市名を入力すると、その都市の現在の天気情報を取得します。
OpenWeatherMap APIを使用しています。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, TypedDict
import requests
from dotenv import load_dotenv

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph

# 環境変数を読み込み
load_dotenv()

# LangSmith 추적 활성화
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "new-agent")

class Configuration(TypedDict):
    """エージェントの設定可能なパラメータ
    
    アシスタント作成時またはグラフ呼び出し時に設定します。
    """
    api_key: str


@dataclass
class State:
    """エージェントの入力状態
    
    入力データの初期構造を定義します。
    """
    city: str = ""
    weather_info: Dict[str, Any] = None
    error: str = ""


async def get_weather_info(state: State, config: RunnableConfig) -> Dict[str, Any]:
    """都市の天気情報を取得する
    
    OpenWeatherMap APIを使用して現在の天気情報を取得します。
    """
    configuration = config.get("configurable", {})
    api_key = configuration.get("api_key") or os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        return {
            "error": "OpenWeatherMap APIキーが設定されていません。環境変数OPENWEATHER_API_KEYを設定するか、設定でapi_keyを指定してください。"
        }
    
    if not state.city:
        return {
            "error": "都市名が入力されていません。"
        }
    
    try:
        # OpenWeatherMap APIから天気情報を取得
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": state.city,
            "appid": api_key,
            "units": "metric",  # 摂氏温度
            "lang": "ja"  # 日本語
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        # APIキーの検証
        if response.status_code == 401:
            return {
                "error": "APIキーが無効です。OpenWeatherMapで有効なAPIキーを取得してください。\n"
                         "https://openweathermap.org/api から無料のAPIキーを発行できます。"
            }
        elif response.status_code == 429:
            return {
                "error": "API制限に達しました。1分後に再試行してください。"
            }
        elif response.status_code == 404:
            return {
                "error": f"都市 '{state.city}' が見つかりません。正しい都市名を入力してください。"
            }
        
        response.raise_for_status()
        
        weather_data = response.json()
        
        # 天気情報を整形
        weather_info = {
            "city": weather_data["name"],
            "country": weather_data["sys"]["country"],
            "temperature": f"{weather_data['main']['temp']}°C",
            "feels_like": f"{weather_data['main']['feels_like']}°C",
            "humidity": f"{weather_data['main']['humidity']}%",
            "pressure": f"{weather_data['main']['pressure']}hPa",
            "description": weather_data["weather"][0]["description"],
            "wind_speed": f"{weather_data['wind']['speed']}m/s",
            "visibility": f"{weather_data.get('visibility', 'N/A')}m"
        }
        
        return {
            "weather_info": weather_info,
            "error": ""
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"APIリクエストエラー: {str(e)}"
        }
    except KeyError as e:
        return {
            "error": f"APIレスポンスの解析エラー: {str(e)}"
        }
    except Exception as e:
        return {
            "error": f"予期しないエラー: {str(e)}"
        }


# グラフを定義
graph = (
    StateGraph(State, config_schema=Configuration)
    .add_node("get_weather", get_weather_info)
    .add_edge("__start__", "get_weather")
    .compile(name="Weather Graph")
)
