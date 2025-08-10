"""天気情報を取得するLangGraph

自然言語の入力から都市名を抽出し、その都市の現在の天気情報を取得します。
OpenWeatherMap APIを使用しています。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, TypedDict
import requests
from dotenv import load_dotenv

from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
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
    openai_api_key: str


@dataclass
class State:
    """エージェントの入力状態
    
    入力データの初期構造を定義します。
    """
    user_input: str = ""  # ユーザーの自然言語入力
    city: str = ""        # 抽出された都市名
    weather_info: Dict[str, Any] = None
    error: str = ""


async def extract_city_from_input(state: State, config: RunnableConfig) -> State:
    """自然言語の入力から都市名を抽出する
    
    LLMを使用してユーザーの入力から都市名を抽出します。
    """
    print(f"🔍 extract_city_from_input 실행됨: user_input='{state.user_input}'")
    
    configuration = config.get("configurable", {})
    openai_api_key = configuration.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("❌ OpenAI API 키가 없음")
        state.error = "OpenAI APIキーが設定されていません。環境変数OPENAI_API_KEYを設定するか、設定でopenai_api_keyを指定してください。"
        return state
    
    if not state.user_input:
        print("❌ 사용자 입력이 없음")
        state.error = "ユーザー入力がありません。"
        return state
    
    try:
        print("🤖 LLM으로 도시명 추출 시도...")
        # OpenAI LLMを初期化
        llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4o-mini",
            temperature=0
        )
        
        # 都市名抽出用のプロンプト
        prompt = ChatPromptTemplate.from_messages([
            ("system", """あなたは都市名を抽出する専門家です。
ユーザーの入力から都市名のみを抽出してください。

例：
- "도쿄の 날씨는 어떤가요?" → "Tokyo"
- "how's the weather in Tokyo?" → "Tokyo"
- "서울 날씨 알려줘" → "Seoul"
- "What's the weather like in Paris?" → "Paris"

都市名が見つからない場合は空文字列を返してください。
都市名のみを返し、説明や追加のテキストは含めないでください。"""),
            ("user", "{user_input}")
        ])
        
        # LLMで都市名を抽出
        chain = prompt | llm
        response = await chain.ainvoke({"user_input": state.user_input})
        
        # レスポンスから都市名を抽出（余分な空白や改行を除去）
        extracted_city = response.content.strip()
        print(f"🏙️ 추출된 도시명: '{extracted_city}'")
        
        if not extracted_city:
            print("❌ 도시명 추출 실패")
            state.error = "入力から都市名を抽出できませんでした。都市名を含む文章を入力してください。"
            return state
        
        # 状態を更新
        state.city = extracted_city
        state.error = ""
        print(f"✅ 도시명 추출 성공: {state.city}")
        return state
        
    except Exception as e:
        print(f"❌ 도시명 추출 에러: {str(e)}")
        # OpenAI API 에러인 경우 구체적인 메시지 제공
        if "401" in str(e) and "API key" in str(e):
            state.error = "OpenAI API 키가 유효하지 않습니다. 올바른 API 키를 설정해주세요."
        else:
            state.error = f"都市名抽出エラー: {str(e)}"
        return state


async def get_weather_info(state: State, config: RunnableConfig) -> State:
    """都市の天気情報を取得する
    
    OpenWeatherMap APIを使用して現在の天気情報を取得します。
    """
    print(f"🌤️ get_weather_info 실행됨: city='{state.city}'")
    
    configuration = config.get("configurable", {})
    api_key = configuration.get("api_key") or os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        print("❌ OpenWeatherMap API 키가 없음")
        state.error = "OpenWeatherMap APIキーが設定されていません。環境変数OPENWEATHER_API_KEYを設定するか、設定でapi_keyを指定してください。"
        return state
    
    if not state.city:
        print("❌ 도시명이 없음")
        state.error = "都市名が入力されていません。"
        return state
    
    try:
        print(f"🌍 {state.city}의 날씨 정보 조회 중...")
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
            print("❌ API 키가 무효함")
            state.error = "APIキーが無効です。OpenWeatherMapで有効なAPIキーを取得してください。\n" + \
                         "https://openweathermap.org/api から無料のAPIキーを発行できます。"
            return state
        elif response.status_code == 429:
            print("❌ API 제한에 도달함")
            state.error = "API制限に達しました。1分後に再試行してください。"
            return state
        elif response.status_code == 404:
            print(f"❌ 도시를 찾을 수 없음: {state.city}")
            state.error = f"都市 '{state.city}' が見つかりません。正しい都市名を入力してください。"
            return state
        
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
        
        # 状態を更新
        state.weather_info = weather_info
        state.error = ""
        print(f"✅ 날씨 정보 조회 성공: {weather_info['city']}")
        return state
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 에러: {str(e)}")
        state.error = f"APIリクエストエラー: {str(e)}"
        return state
    except KeyError as e:
        print(f"❌ API 응답 파싱 에러: {str(e)}")
        state.error = f"APIレスポンスの解析エラー: {str(e)}"
        return state
    except Exception as e:
        print(f"❌ 예상치 못한 에러: {str(e)}")
        state.error = f"予期しないエラー: {str(e)}"
        return state


# グラフを定義
graph = (
    StateGraph(State, config_schema=Configuration)
    .add_node("extract_city", extract_city_from_input)  # 都市名抽出ノード
    .add_node("get_weather", get_weather_info)          # 天気情報取得ノード
    .add_edge("__start__", "extract_city")              # 開始 → 都市名抽出
    .add_edge("extract_city", "get_weather")            # 都市名抽出 → 天気情報取得
    .set_entry_point("extract_city")                    # エントリーポイントを明示的に設定
    .compile(name="Weather Graph")
)
