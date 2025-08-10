#!/usr/bin/env python3
"""天気グラフの使用例

自然言語の入力から都市名を抽出し、天気情報を取得する例を示します。
"""

import asyncio
import os
from dotenv import load_dotenv
from src.agent.graph import graph, State

# 環境変数を読み込み
load_dotenv()

async def main():
    """メイン関数"""
    print("🌤️  天気情報取得システム")
    print("=" * 50)
    print("💡 自然言語で都市の天気を聞いてみてください！")
    print("例:")
    print("  - '도쿄の 날씨는 어떤가요?'")
    print("  - 'how's the weather in Tokyo?'")
    print("  - '서울 날씨 알려줘'")
    print("  - 'What's the weather like in Paris?'")
    print()
    
    # 自然言語の入力を取得
    user_input = input("質問を入力してください: ").strip()
    
    if not user_input:
        print("❌ 入力がありません。")
        return
    
    # 初期状態を作成
    initial_state = State(user_input=user_input)
    
    try:
        # グラフを実行
        print(f"\n🔍 入力を分析して天気情報を取得中...")
        
        # APIキーを設定で渡す（環境変数から取得）
        config = {
            "configurable": {
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "api_key": os.getenv("OPENWEATHER_API_KEY")
            }
        }
        
        result = await graph.ainvoke(initial_state, config)
        
        # 結果を表示
        if result.get("error"):
            print(f"❌ エラー: {result['error']}")
        elif result.get("weather_info"):
            weather = result["weather_info"]
            print(f"\n✅ {weather['city']}, {weather['country']}の天気情報:")
            print(f"🌡️  気温: {weather['temperature']}")
            print(f"🌡️  体感温度: {weather['feels_like']}")
            print(f"💧 湿度: {weather['humidity']}")
            print(f"🌪️  風速: {weather['wind_speed']}")
            print(f"👁️  視界: {weather['visibility']}")
            print(f"📊 気圧: {weather['pressure']}")
            print(f"☁️  天気: {weather['description']}")
        else:
            print("❌ 予期しない結果が返されました。")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    # 非同期関数を実行
    asyncio.run(main()) 