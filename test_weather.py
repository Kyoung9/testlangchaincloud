#!/usr/bin/env python3
"""天気グラフのテストスクリプト

自然言語入力から都市名을抽出し、天気情報を取得する機能をテストします。
"""

import asyncio
from src.agent.graph import graph, State

async def test_weather_graph():
    """天気グラフのテスト"""
    print("🧪 天気グラフのテスト")
    print("=" * 40)
    
    # 1. グラフの基本情報を表示
    print(f"📊 グラフ名: {graph.name}")
    print(f"🔧 設定スキーマ: {graph.config_schema}")
    print(f"📝 状態クラス: {State}")
    
    # 2. OpenAI APIキーなしでテスト（에러 핸들링）
    print("\n🔍 テスト1: OpenAI API키 없음")
    initial_state = State(user_input="도쿄의 날씨는 어떤가요?")
    config = {"configurable": {"api_key": "test_key"}}  # OpenWeatherMap API키만 있음
    
    try:
        result = await graph.ainvoke(initial_state, config)
        if result.get("error"):
            print(f"✅ 에러 핸들링 성공: {result['error']}")
        else:
            print(f"❌ 예상치 못한 결과: {result}")
    except Exception as e:
        print(f"❌ 에러: {e}")
    
    # 3. OpenWeatherMap API키 없음으로 테스트
    print("\n🔍 テスト2: OpenWeatherMap API키 없음")
    initial_state = State(user_input="how's the weather in Tokyo?")
    config = {"configurable": {"openai_api_key": "test_openai_key"}}  # OpenAI API키만 있음
    
    try:
        result = await graph.ainvoke(initial_state, config)
        if result.get("error"):
            print(f"✅ 에러 핸들링 성공: {result['error']}")
        else:
            print(f"❌ 예상치 못한 결과: {result}")
    except Exception as e:
        print(f"❌ 에러: {e}")
    
    # 4. 사용자 입력 없음으로 테스트
    print("\n🔍 テスト3: 사용자 입력 없음")
    initial_state = State(user_input="")
    config = {"configurable": {"openai_api_key": "test_key", "api_key": "test_key"}}
    
    try:
        result = await graph.ainvoke(initial_state, config)
        if result.get("error"):
            print(f"✅ 에러 핸들링 성공: {result['error']}")
        else:
            print(f"❌ 예상치 못한 결과: {result}")
    except Exception as e:
        print(f"❌ 에러: {e}")
    
    # 5. 한국어 입력 테스트
    print("\n🔍 テスト4: 한국어 입력")
    initial_state = State(user_input="서울 날씨 알려줘")
    config = {"configurable": {"openai_api_key": "test_key", "api_key": "test_key"}}
    
    try:
        result = await graph.ainvoke(initial_state, config)
        print(f"📋 결과: {result}")
    except Exception as e:
        print(f"❌ 에러: {e}")
    
    # 6. 영어 입력 테스트
    print("\n🔍 テスト5: 영어 입력")
    initial_state = State(user_input="What's the weather like in Paris?")
    config = {"configurable": {"openai_api_key": "test_key", "api_key": "test_key"}}
    
    try:
        result = await graph.ainvoke(initial_state, config)
        print(f"📋 결과: {result}")
    except Exception as e:
        print(f"❌ 에러: {e}")
    
    print("\n🎉 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_weather_graph()) 