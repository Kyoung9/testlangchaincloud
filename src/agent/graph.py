"""天気情報を取得するLangGraph

自然言語の入力から都市名を抽出し、その都市の現在の天気情報を取得します。
OpenWeatherMap APIを使用しています。

外部からの呼び出しに対応:
- messages/query形式の入力
- city_hintによる直接都市名指定
- configurable設定によるAPIキー管理
- Universal Callerとの完全互換性
"""

from __future__ import annotations

import os
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, TypedDict, List, Optional
import aiohttp
from dotenv import load_dotenv

from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field

# 環境変数を読み込み
load_dotenv()

# 環境変数のデバッグ出力
print(f"🔧 環境変数確認:")
print(f"   OPENWEATHER_API_KEY: {'設定済み' if os.getenv('OPENWEATHER_API_KEY') else '未設定'}")
print(f"   OPENAI_API_KEY: {'設定済み' if os.getenv('OPENAI_API_KEY') else '未設定'}")

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

class InputSchema(BaseModel):
    """外部からの入力スキーマ
    
    Universal Callerからの呼び出しに対応します。
    """
    messages: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="メッセージ配列 (role: user/assistant, content: メッセージ内容)"
    )
    query: Optional[str] = Field(
        default="",
        description="クエリ文字列"
    )
    city: Optional[str] = Field(
        default="",
        description="都市名ヒント (city_hint)"
    )

@dataclass
class State:
    """エージェントの入力状態
    
    入力データの初期構造を定義します。
    """
    messages: List[Dict[str, str]] = None  # 外部からのメッセージ配列
    query: str = ""                        # 外部からのクエリ
    user_input: str = ""                   # 処理用のユーザー入力
    city: str = ""                         # 抽出された都市名または外部からのcity_hint
    weather_info: Dict[str, Any] = None    # 天気情報
    error: str = ""                        # エラーメッセージ
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []
        # messagesからuser_inputを抽出
        if self.messages and not self.user_input:
            for msg in self.messages:
                if msg.get("role") == "user":
                    self.user_input = msg.get("content", "")
                    break
        # queryからuser_inputを抽出（messagesがない場合）
        if not self.user_input and self.query:
            self.user_input = self.query


async def extract_city_from_input(state: State, config: RunnableConfig) -> State:
    """自然言語の入力から都市名を抽出する
    
    LLMを使用してユーザーの入力から都市名を抽出します。
    外部からcity_hintが提供された場合はそれを優先使用します。
    """
    print(f"🔍 extract_city_from_input 実行中: user_input='{state.user_input}', city_hint='{state.city}'")
    
    configuration = config.get("configurable", {})
    openai_api_key = configuration.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
    
    # 外部からcity_hintが提供された場合はLLM処理をスキップ
    if state.city and state.city.strip():
        print(f"🏙️ 外部から提供された都市名を使用: {state.city}")
        return state
    
    if not openai_api_key:
        print("❌ OpenAI API キーがありません")
        state.error = "OpenAI APIキーが設定されていません。環境変数OPENAI_API_KEYを設定するか、設定でopenai_api_keyを指定してください。"
        return state
    
    if not state.user_input:
        print("❌ ユーザー入力がありません")
        state.error = "ユーザー入力がありません。都市名を含む文章を入力するか、city_hintを指定してください。"
        return state
    
    try:
        print("🤖 LLMで都市名抽出を試行中...")
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
        print(f"🏙️ 抽出された都市名: '{extracted_city}'")
        
        if not extracted_city:
            print("❌ 都市名抽出に失敗しました")
            state.error = "入力から都市名を抽出できませんでした。都市名を含む文章を入力するか、city_hintを指定してください。"
            return state
        
        # 状態を更新
        state.city = extracted_city
        state.error = ""
        print(f"✅ 都市名抽出成功: {state.city}")
        return state
        
    except Exception as e:
        print(f"❌ 都市名抽出エラー: {str(e)}")
        # OpenAI API エラーの場合、具体的なメッセージを提供
        if "401" in str(e) and "API key" in str(e):
            state.error = "OpenAI API キーが無効です。正しいAPI キーを設定してください。"
        elif "rate_limit" in str(e).lower() or "429" in str(e):
            state.error = "OpenAI API制限に達しました。しばらく待ってから再試行してください。"
        else:
            state.error = f"都市名抽出エラー: {str(e)}"
        return state


async def get_weather_info(state: State, config: RunnableConfig) -> State:
    """都市の天気情報を取得する
    
    OpenWeatherMap APIを使用して現在の天気情報を取得します。
    """
    print(f"🌤️ get_weather_info 実行中: city='{state.city}'")
    
    configuration = config.get("configurable", {})
    api_key = configuration.get("api_key") or os.getenv("OPENWEATHER_API_KEY")
    
    print(f"🔑 API キー確認:")
    print(f"   configurable.api_key: {configuration.get('api_key', '未設定')}")
    print(f"   OPENWEATHER_API_KEY: {os.getenv('OPENWEATHER_API_KEY', '未設定')}")
    print(f"   使用するキー: {api_key[:8]}..." if api_key else "キーなし")
    
    if not api_key:
        print("❌ OpenWeatherMap API キーが設定されていません")
        state.error = "OpenWeatherMap APIキーが設定されていません。環境変数OPENWEATHER_API_KEYを設定するか、設定でapi_keyを指定してください。\n\nhttps://openweathermap.org/api から無料のAPIキーを発行できます。"
        return state
    
    if not state.city or not state.city.strip():
        print("❌ 都市名が空です")
        state.error = "都市名が入力されていません。都市名を含む文章を入力するか、city_hintを指定してください。"
        return state
    
    try:
        print(f"🌍 {state.city}の天気情報を取得中...")
        # OpenWeatherMap APIから天気情報を取得
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": state.city,
            "appid": api_key,
            "units": "metric",  # 摂氏温度
            "lang": "ja"  # 日本語
        }
        
        print(f"📡 API リクエスト詳細:")
        print(f"   URL: {url}")
        print(f"   City: {state.city}")
        print(f"   API Key: {api_key[:8]}...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                print(f"📡 API レスポンス: {response.status}")
                print(f"   Response Headers: {dict(response.headers)}")
                
                # レスポンス本文を確認
                response_text = await response.text()
                print(f"   Response Body: {response_text[:200]}...")
                
                # APIキーの検証とエラーハンドリング
                if response.status == 401:
                    print("❌ API キーが無効です")
                    print(f"   レスポンス本文: {response_text}")
                    state.error = "OpenWeatherMap APIキーが無効です。OpenWeatherMapで有効なAPIキーを取得してください。\n\nhttps://openweathermap.org/api から無料のAPIキーを発行できます。"
                    return state
                elif response.status == 429:
                    print("❌ API制限に達しました")
                    state.error = "OpenWeatherMap API制限に達しました。1分後に再試行してください。"
                    return state
                elif response.status == 404:
                    print(f"❌ 都市が見つかりません: {state.city}")
                    state.error = f"都市 '{state.city}' が見つかりません。\n\n以下の点を確認してください：\n• 都市名のスペルが正しいか\n• 都市名が英語表記になっているか\n• 都市名が一般的に認識されているか\n\n例：'Tokyo', 'Seoul', 'Paris', 'New York'"
                    return state
                elif response.status >= 500:
                    print(f"❌ サーバーエラー: {response.status}")
                    state.error = f"OpenWeatherMapサーバーエラー ({response.status})。しばらく待ってから再試行してください。"
                    return state
                
                response.raise_for_status()
                weather_data = await response.json()
        
        # 天気情報の検証と整形
        try:
            weather_info = {
                "city": weather_data.get("name", state.city),
                "country": weather_data.get("sys", {}).get("country", "N/A"),
                "temperature": f"{weather_data.get('main', {}).get('temp', 'N/A')}°C",
                "feels_like": f"{weather_data.get('main', {}).get('feels_like', 'N/A')}°C",
                "humidity": f"{weather_data.get('main', {}).get('humidity', 'N/A')}%",
                "pressure": f"{weather_data.get('main', {}).get('pressure', 'N/A')}hPa",
                "description": weather_data.get("weather", [{}])[0].get("description", "N/A"),
                "wind_speed": f"{weather_data.get('wind', {}).get('speed', 'N/A')}m/s",
                "visibility": f"{weather_data.get('visibility', 'N/A')}m"
            }
            
            # データの妥当性チェック
            if weather_info["temperature"] == "N/A°C":
                print("⚠️ 温度データが取得できませんでした")
                weather_info["temperature"] = "データなし"
            
            if weather_info["description"] == "N/A":
                print("⚠️ 天気説明が取得できませんでした")
                weather_info["description"] = "データなし"
            
        except (KeyError, IndexError) as e:
            print(f"❌ 天気データの解析エラー: {str(e)}")
            state.error = f"天気データの解析エラー: {str(e)}"
            return state
        
        # 状態を更新
        state.weather_info = weather_info
        state.error = ""
        print(f"✅ 天気情報取得成功: {weather_info['city']}")
        return state
        
    except aiohttp.ClientError as e:
        print(f"❌ API リクエストエラー: {str(e)}")
        state.error = f"OpenWeatherMap APIリクエストエラー: {str(e)}\n\nネットワーク接続を確認してください。"
        return state
    except asyncio.TimeoutError:
        print("❌ API リクエストがタイムアウトしました")
        state.error = "OpenWeatherMap APIへのリクエストがタイムアウトしました。ネットワーク接続を確認してください。"
        return state
    except Exception as e:
        print(f"❌ 予期しないエラー: {str(e)}")
        state.error = f"予期しないエラー: {str(e)}\n\n技術的な問題が発生しました。しばらく待ってから再試行してください。"
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

# 外部からの呼び出し用のエントリーポイント
async def invoke_graph(
    input_data: InputSchema,
    config: Optional[Configuration] = None
) -> Dict[str, Any]:
    """外部からの呼び出し用のエントリーポイント
    
    Universal Callerからの呼び出しに対応します。
    """
    try:
        # 入力データをStateに変換
        state = State(
            messages=input_data.messages or [],
            query=input_data.query or "",
            city=input_data.city or ""
        )
        
        # 設定を準備
        runnable_config = RunnableConfig(
            configurable=config or {},
            input_schema=InputSchema
        )
        
        # グラフを実行
        result = await graph.ainvoke(
            state,
            config=runnable_config
        )
        
        # 結果を整形
        if result.error:
            return {
                "status": "error",
                "error": result.error
            }
        else:
            return {
                "status": "success",
                "city": result.city,
                "weather_info": result.weather_info,
                "message": f"{result.weather_info['city']}の現在の天気: {result.weather_info['description']}, 気温: {result.weather_info['temperature']}, 湿度: {result.weather_info['humidity']}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": f"予期しないエラー: {str(e)}"
        }
