#!/usr/bin/env python3
"""天気グラフの使用例

このスクリプトは、作成した天気グラフの使用方法を示します。
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
    
    # 都市名を入力
    city = input("都市名を入力してください (例: Tokyo, New York, London): ").strip()
    
    if not city:
        print("❌ 都市名が入力されていません。")
        return
    
    # 初期状態を作成
    initial_state = State(city=city)
    
    try:
        # グラフを実行
        print(f"\n🔍 {city}の天気情報を取得中...")
        
        # APIキーを設定で渡す（環境変数から取得）
        config = {
            "configurable": {
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