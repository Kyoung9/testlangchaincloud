# 🌤️ 天気情報取得 LangGraph プロジェクト - プロジェクト概要

## 📋 プロジェクト概要

このプロジェクトは、LangGraphを使用して都市名を入力として受け取り、OpenWeatherMap APIから現在の天気情報を取得するシステムです。

## 🏗️ アーキテクチャ

```
src/agent/
├── __init__.py          # パッケージ初期化
└── graph.py             # メインの天気グラフ定義
```

### 主要コンポーネント

1. **State**: 都市名、天気情報、エラー情報を管理
2. **Configuration**: APIキーの設定
3. **get_weather_info**: 天気情報を取得するメインノード
4. **Weather Graph**: 単一ノードのLangGraph

## 🚀 使用方法

### 1. 環境設定

```bash
# 依存関係のインストール
pip install -e .

# 環境変数ファイルの作成
cp .env.example .env

# .envファイルにAPIキーを設定
OPENWEATHER_API_KEY=your_actual_api_key
```

### 2. 基本的な使用

```python
import asyncio
from src.agent.graph import graph, State

async def get_weather(city: str):
    initial_state = State(city=city)
    config = {
        "configurable": {
            "api_key": "your_api_key"
        }
    }
    
    result = await graph.ainvoke(initial_state, config)
    return result

# 使用例
weather = await get_weather("Tokyo")
```

### 3. コマンドラインでの使用

```bash
python example_usage.py
```

## 🔧 機能

- ✅ 都市名による天気情報取得
- ✅ 気温、湿度、気圧、風速などの詳細情報
- ✅ 日本語での天気説明
- ✅ エラーハンドリング
- ✅ 非同期処理
- ✅ 設定可能なAPIキー

## 📊 取得される天気情報

- 🌡️ 気温 (摂氏)
- 🌡️ 体感温度
- 💧 湿度 (%)
- 📊 気圧 (hPa)
- ☁️ 天気の説明
- 🌪️ 風速 (m/s)
- 👁️ 視界 (m)
- 🌍 都市名・国名

## 🧪 テスト

```bash
# 基本的なテスト
python test_weather.py

# 使用例の実行
python example_usage.py
```

## 🌐 API設定

OpenWeatherMap APIを使用しています：
- 無料プラン: 1分間に60回のリクエスト制限
- 温度単位: 摂氏 (metric)
- 言語: 日本語 (ja)

## 📁 ファイル構成

```
.
├── src/agent/
│   ├── __init__.py          # パッケージ初期化
│   └── graph.py             # メインの天気グラフ
├── example_usage.py         # 使用例スクリプト
├── test_weather.py          # テストスクリプト
├── .env.example             # 環境変数設定例
├── pyproject.toml           # プロジェクト設定
└── README.md                # 詳細なドキュメント
```

## 🔮 今後の拡張可能性

1. **複数都市の同時取得**: バッチ処理による複数都市の天気情報取得
2. **予報情報の追加**: 5日間予報や時間別予報の取得
3. **地理情報の統合**: 座標ベースの天気情報取得
4. **通知システム**: 特定の天気条件での通知機能
5. **データベース統合**: 天気履歴の保存と分析

## ⚠️ 注意事項

- APIキーは機密情報です。`.env`ファイルに保存し、Gitにコミットしないでください
- 無料プランのAPI制限に注意してください
- 都市名は英語で入力することを推奨します

## 🆘 トラブルシューティング

### よくある問題

1. **APIキーエラー**: `.env`ファイルの設定を確認
2. **都市名エラー**: 英語での都市名入力を確認
3. **ネットワークエラー**: インターネット接続を確認

### デバッグ

```bash
# 詳細なログ出力
python -u test_weather.py

# LangGraph Studioでの視覚的デバッグ
langgraph dev
```

---

このプロジェクトは、LangGraphの基本概念を学び、実用的な天気情報取得システムを構築するための素晴らしい出発点です。 