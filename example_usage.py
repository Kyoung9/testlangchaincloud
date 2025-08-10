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
    print("💡 自然言語で都市의 날씨를 물어보세요!")
    print("예시:")
    print("  - '도쿄의 날씨는 어떤가요?'")
    print("  - 'how's the weather in Tokyo?'")
    print("  - '서울 날씨 알려줘'")
    print("  - 'What's the weather like in Paris?'")
    print()
    
    # 自然言語の入力を取得
    user_input = input("질문을 입력하세요: ").strip()
    
    if not user_input:
        print("❌ 입력이 없습니다.")
        return
    
    # 初期状態を作成
    initial_state = State(user_input=user_input)
    
    try:
        # グラフを実行
        print(f"\n🔍 입력을 분석하고 날씨 정보를 가져오는 중...")
        
        # API키를 설정으로 전달（환경변수에서 가져옴）
        config = {
            "configurable": {
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "api_key": os.getenv("OPENWEATHER_API_KEY")
            }
        }
        
        result = await graph.ainvoke(initial_state, config)
        
        # 結果を表示
        if result.get("error"):
            print(f"❌ 에러: {result['error']}")
        elif result.get("weather_info"):
            weather = result["weather_info"]
            print(f"\n✅ {weather['city']}, {weather['country']}의 날씨 정보:")
            print(f"🌡️  기온: {weather['temperature']}")
            print(f"🌡️  체감온도: {weather['feels_like']}")
            print(f"💧 습도: {weather['humidity']}")
            print(f"🌪️  풍속: {weather['wind_speed']}")
            print(f"👁️  가시거리: {weather['visibility']}")
            print(f"📊 기압: {weather['pressure']}")
            print(f"☁️  날씨: {weather['description']}")
        else:
            print("❌ 예상치 못한 결과가 반환되었습니다.")
            
    except Exception as e:
        print(f"❌ 에러가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    # 非同期関数を実行
    asyncio.run(main()) 