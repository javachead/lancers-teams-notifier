# config_advanced.py - 高度な設定ファイル

import os

# 基本設定
LANCERS_SEARCH_URL = "https://www.lancers.jp/work/search/system?budget_from=&budget_to=&work_rank%5B%5D=&work_rank%5B%5D=&work_rank%5B%5D=&keyword=&sort=work_post_date"
MAX_JOBS_TO_FETCH = 100
HEADLESS_MODE = True
TIMEOUT_MS = 60000

# Teams設定
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL", "")
NOTIFICATION_TITLE = "🚀 Lancers週次案件通知"
NOTIFICATION_COLOR = "28A745"  # 緑色

# 弊社スキルセット（優先度付き）
COMPANY_SKILLS = {
    "高優先度": [
        "AI", "GPT", "Python", "API", "Django", 
        "Next.js", "TypeScript", "Java", "機械学習"
    ],
    "中優先度": [
        "Talend", "コンサル", "開発", "システム開発",
        "React", "Node.js", "PostgreSQL", "MySQL"
    ],
    "低優先度": [
        "Render", "ロリッポップ", "WordPress", "PHP"
    ]
}

# 除外キーワード（求人・コンペ・デザイン系を除外）
EXCLUDE_KEYWORDS = [
    # 求人関連
    "求人", "採用", "転職", "正社員", "アルバイト", "派遣",
    
    # コンペ関連
    "コンペ", "コンペティション", "コンテスト", "募集",
    
    # デザイン関連（システム開発以外）
    "ロゴ", "デザイン", "バナー", "チラシ", "名刺", 
    "イラスト", "写真", "動画編集", "音声", "BGM",
    
    # その他除外
    "テスト", "練習", "サンプル", "学習", "勉強"
]

# 必須条件
REQUIRED_CONDITIONS = ["募集中", "応募受付中"]

# 価格フィルタ（最低金額）
MIN_PRICE_FILTER = 30000  # 3万円以上

# スキルマッチング設定
SKILL_MATCH_WEIGHTS = {
    "高優先度": 10,
    "中優先度": 5,
    "低優先度": 2
}

# 急募案件の追加ポイント
URGENT_BONUS = 3

# ファイル設定
DATA_DIR = "data"
JOBS_DATA_PREFIX = "jobs_data"
TEAMS_MESSAGE_FILE = "teams_message.txt"

# ログ設定
LOG_LEVEL = "INFO"
LOG_FILE = "lancers_notifier.log"

# ユーザーエージェント
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 実行時間設定（毎週火曜日16:00）
SCHEDULE_DAY = "tuesday"
SCHEDULE_TIME = "16:00"