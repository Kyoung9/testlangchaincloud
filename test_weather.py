#!/usr/bin/env python3
"""天気グラフのテストスクリプト

APIキーなしでグラフの構造とエラーハンドリングをテストします。
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
    
    # 2. 都市名なしでテスト（エラーハンドリング）
    print("\n🔍 テスト1: 都市名なし")
    initial_state = State(city="")
    config = {"configurable": {"api_key": "test_key"}}
    
    try:
        result = await graph.ainvoke(initial_state, config)
        if result.get("error"):
            print(f"✅ エラーハンドリング成功: {result['error']}")
        else:
            print(f"❌ 予期しない結果: {result}")
    except Exception as e:
        print(f"❌ エラー: {e}")
    
    # 3. APIキーなしでテスト
    print("\n🔍 テスト2: APIキーなし")
    initial_state = State(city="Tokyo")
    config = {"configurable": {}}
    
    try:
        result = await graph.ainvoke(initial_state, config)
        if result.get("error"):
            print(f"✅ エラーハンドリング成功: {result['error']}")
        else:
            print(f"❌ 予期しない結果: {result}")
    except Exception as e:
        print(f"❌ エラー: {e}")
    
    # 4. 正常な状態のテスト（APIキーなしなのでエラーになるはず）
    print("\n🔍 テスト3: 正常な状態")
    initial_state = State(city="Tokyo")
    config = {"configurable": {"api_key": "invalid_key"}}
    
    try:
        result = await graph.ainvoke(initial_state, config)
        print(f"📋 結果: {result}")
    except Exception as e:
        print(f"❌ エラー: {e}")
    
    print("\n🎉 テスト完了!")

if __name__ == "__main__":
    asyncio.run(test_weather_graph()) 