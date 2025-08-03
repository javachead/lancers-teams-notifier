# 🚀 Lancers案件通知システム

弊社のスキルセットに特化したLancers案件の自動取得・Teams通知システムです。

## ✨ 機能概要

- 🎯 **スキルマッチング**: 弊社技術スタックに合致する案件を優先表示
- 📱 **Teams自動通知**: Microsoft Teams Webhookでリアルタイム通知
- 🔧 **詳細スキル分析**: 超高・高・中・低優先度でスキル分類
- 📊 **28KB最大活用**: Teams文字数制限まで最大案件数を表示
- 💾 **データ保存**: JSON形式で履歴管理・分析可能
- ⏰ **定期実行**: 毎週火曜日16:00自動実行

## 🎯 対象スキルセット

### 🔥 超高優先度（100点）
- AI、GPT、ChatGPT、Python、API
- Django、Next.js、TypeScript、機械学習

### ★ 高優先度（50点）  
- bot、Talend、Java、スマホアプリ
- モバイル開発、人工知能

### ◆ 中優先度（20点）
- 効率化、ツール、開発、システム開発
- React、Node.js、自動化、スクレイピング

### ◇ 低優先度（10点）
- PostgreSQL、MySQL、社内ツール
- 業務改善、アプリ、サイト、管理

## 📦 インストール

### 必要な環境
- Python 3.11+
- Windows 10/11
- Microsoft Teams（Webhook設定済み）

### セットアップ

```bash
# リポジトリクローン
git clone https://github.com/your-org/lancers-teams-notifier.git
cd lancers-teams-notifier

# 仮想環境作成・アクティベート
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 依存関係インストール
pip install -r requirements.txt

# Playwrightブラウザインストール
playwright install
```

### 環境設定

1. **Teams Webhook URL取得**
   - Microsoft Teams → チャンネル → コネクタ → Incoming Webhook
   - Webhook URLをコピー

2. **.envファイル作成**
```bash
# .env
TEAMS_WEBHOOK_URL=https://your-teams-webhook-url-here
```

3. **設定確認**
```bash
# Teams接続テスト
python test_teams.py
```

## 🚀 使用方法

### 手動実行
```bash
# 仮想環境アクティベート
.venv\Scripts\activate

# メインスクリプト実行
python fetch_lancers_complete_fixed.py
```

### 定期実行設定（Windows）
```bash
# 管理者権限でPowerShell開く
# 毎週火曜日16:00に自動実行
schtasks /create /tn "LancersWeeklyNotifier" /tr "\"C:\path\to\project\.venv\Scripts\python.exe\" \"C:\path\to\project\fetch_lancers_complete_fixed.py\"" /sc weekly /d TUE /st 16:00 /f

# タスク確認
schtasks /query /tn "LancersWeeklyNotifier"

# 手動テスト実行
schtasks /run /tn "LancersWeeklyNotifier"
```

## 📊 出力例

### コンソール出力
```
🚀 Lancers全案件取得を開始...
📡 アクセス中: https://www.lancers.jp/work/search/system
✅ ページ読み込み完了 (ステータス: 200)
📊 67 個の案件候補を発見
📝 案件 1: 【完全在宅】ChatGPT・AI活用サポート... | 🔧 スキルセット: 🔥AI,GPT,ChatGPT
📝 案件 2: 【Python】申込書作成自動化... | 🔧 スキルセット: 🔥Python ◆自動化
✅ 全 24 件の案件を取得しました

📊 Teams表示制限: 25,000文字まで利用可能
📊 実際の文字数: 18,247文字 / 25,000文字 (73.0%)
📊 表示案件数: 24件 / 24件
```

### Teams通知例
```
🚀 Lancers全案件リスト (24件発見 / 24件表示) - 2025/08/03 13:57

現在の全案件リストです（24件を発見）

1. 【完全在宅】ChatGPT・AI活用サポート担当募集
💰 10,000円 ~ 20,000円 / 固定
🔧 スキルセット: 🔥AI,GPT,ChatGPT
🔗 詳細

2. 【Python】申込書作成から社内申請までの自動化依頼
💰 50,000円 ~ 60,000円 / 固定  
🔧 スキルセット: 🔥Python ◆自動化
🔗 詳細
```

## 📁 ファイル構成

```
lancers-teams-notifier/
├── fetch_lancers_complete_fixed.py  # メインスクリプト
├── test_teams.py                    # Teams接続テスト
├── config.py                        # 設定ファイル
├── requirements.txt                 # 依存関係
├── .env                            # 環境変数（要作成）
├── .gitignore                      # Git除外設定
├── README.md                       # このファイル
└── data/
    ├── all_jobs_YYYYMMDD_HHMM.json # 取得データ（自動生成）
    └── teams_message.txt           # Teams送信内容（自動生成）
```

## ⚙️ 設定カスタマイズ

### スキルセット変更
```python
# fetch_lancers_complete_fixed.py内
# 弊社スキルセット（優先度付き）
COMPANY_SKILLS = {
    "高優先度": ["AI","Ai","人工知能","bot","GPT", "ChatGPT", "Python","Talend", "API", "Django", "Next.js", "TypeScript", "Java", "機械学習", "スマホアプリ", "モバイル開発"],
    "中優先度": ["効率化","ツール", "コンサル", "開発", "システム開発", "React", "Node.js", "PostgreSQL", "MySQL", "社内ツール", "業務改善"],
    "低優先度": ["Render", "ロリッポップ", "WordPress", "PHP"],
}
```

### 除外キーワード追加
EXCLUDE_KEYWORDS = [
    "求人", "採用", "転職", "正社員", "アルバイト", "派遣",
    "コンペ", "コンペティション", "コンテスト", "募集",
    "ロゴ", "デザイン", "バナー", "チラシ", "名刺", "イラスト", 
    "写真", "動画編集", "音声", "BGM", "テスト", "練習", "サンプル",
    "募集終了", "締切", "CAD",
]
```

### 取得件数変更
```python
MAX_JOBS_TO_FETCH = 100  # 取得上限数
```

## 🔧 トラブルシューティング

### よくある問題

**1. Teams送信失敗**
```bash
# Webhook URL確認
echo $TEAMS_WEBHOOK_URL  # Linux/Mac
echo %TEAMS_WEBHOOK_URL%  # Windows

# 接続テスト
python test_teams.py
```

**2. Playwright起動失敗**
```bash
# ブラウザ再インストール
playwright install --force
```

**3. 案件が取得できない**
```bash
# ヘッドレスモード無効化（デバッグ用）
# fetch_lancers_complete_fixed.py内
HEADLESS_MODE = False
```

**4. 文字化け**
```bash
# コンソール文字コード確認（Windows）
chcp 65001
```

### ログ確認
```bash
# 生成されたJSONファイル確認
cat all_jobs_*.json | jq .count  # 取得件数確認
cat all_jobs_*.json | jq '.jobs[0]'  # 最初の案件詳細
```

## 📈 システム統計

実行結果例：
- **全案件数**: 24件
- **スキルマッチ率**: 58.3%
- **複数スキルマッチ**: 14件
- **高優先度案件**: 14件
- **Teams文字数使用率**: 73.0%

## 🤝 貢献

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🔗 関連リンク

- [Lancers](https://www.lancers.jp/)
- [Microsoft Teams Webhooks](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)
- [Playwright Documentation](https://playwright.dev/python/)

---
