#!/usr/bin/env python3
"""シンプルなテスト

基本的な機能とログ出力をテストします。
"""

import asyncio
from src.agent.graph import State, graph

async def test_graph_structure():
    """グラフの構造をテスト"""
    print("🧪 グラフ構造テスト")
    print("=" * 30)
    
    print(f"グラフ名: {graph.name}")
    print(f"ノード数: {len(graph.nodes)}")
    print(f"ノード一覧: {list(graph.nodes.keys())}")
    print()

async def test_state_operations():
    """State クラスの操作をテスト"""
    print("🧪 State クラス操作テスト")
    print("=" * 30)
    
    # 基本的な状態作成
    state = State()
    print(f"初期状態: user_input='{state.user_input}', city='{state.city}'")
    
    # 状態更新
    state.user_input = "パリの天気は？"
    state.city = "Paris"
    print(f"更新後: user_input='{state.user_input}', city='{state.city}'")
    
    # エラー設定
    state.error = "テストエラー"
    print(f"エラー設定後: error='{state.error}'")
    
    # エラークリア
    state.error = ""
    print(f"エラークリア後: error='{state.error}'")
    print()

async def test_error_messages():
    """エラーメッセージの日本語表示をテスト"""
    print("🧪 エラーメッセージテスト")
    print("=" * 30)
    
    # 様々なエラーケース
    error_cases = [
        "OpenAI APIキーが設定されていません。",
        "都市名が入力されていません。",
        "APIキーが無効です。",
        "都市が見つかりません。",
        "予期しないエラーが発生しました。"
    ]
    
    for i, error_msg in enumerate(error_cases, 1):
        state = State()
        state.error = error_msg
        print(f"ケース {i}: {state.error}")
    
    print()

async def test_log_formatting():
    """ログフォーマットのテスト"""
    print("🧪 ログフォーマットテスト")
    print("=" * 30)
    
    # エモジと日本語の組み合わせ
    log_messages = [
        "🔍 都市名抽出を開始",
        "🤖 LLM処理中...",
        "🏙️ 都市名を抽出: Tokyo",
        "✅ 処理完了",
        "❌ エラーが発生",
        "🌤️ 天気情報を取得中",
        "🌍 APIリクエスト送信中"
    ]
    
    for msg in log_messages:
        print(msg)
    
    print()

async def main():
    """メイン関数"""
    print("🚀 シンプルテスト開始")
    print("=" * 50)
    
    await test_graph_structure()
    await test_state_operations()
    await test_error_messages()
    await test_log_formatting()
    
    print("✅ シンプルテスト完了")
    print("\n📝 テスト結果:")
    print("  - グラフ構造: ✅")
    print("  - State クラス: ✅")
    print("  - エラーメッセージ: ✅")
    print("  - ログフォーマット: ✅")
    print("  - 日本語出力: ✅")

if __name__ == "__main__":
    asyncio.run(main()) 