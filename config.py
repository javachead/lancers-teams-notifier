# config.py - 設定ファイル

import os

# Lancers関連設定
LANCERS_BASE_URL = "https://www.lancers.jp"
LANCERS_SEARCH_URL = "https://www.lancers.jp/work/search/system?budget_from=&budget_to=&work_rank%5B%5D=&work_rank%5B%5D=&work_rank%5B%5D=&keyword=&sort=work_post_date"

# Teams通知設定
# 環境変数から取得、なければ空文字
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL", "")

# 通知設定
ENABLE_TEAMS_NOTIFICATION = True  # Falseにすると通知を無効化
NOTIFICATION_TITLE = "🚀 Lancers新着案件通知"
NOTIFICATION_COLOR = "0078D4"  # Microsoft Blue

# スクレイピング設定
MAX_JOBS_TO_FETCH = 10
TIMEOUT_MS = 30000
HEADLESS_MODE = True  # 本番環境ではTrue、デバッグ時はFalse
SLOW_MO = 1000  # ミリ秒

# ファイルパス
JOBS_DATA_FILE = "jobs_data.json"
TEAMS_MESSAGE_FILE = "teams_message.txt"
DEBUG_SCREENSHOT = "debug_page.png"
ERROR_SCREENSHOT = "error_screenshot.png"
DEBUG_HTML = "debug_page.html"

# セレクタ候補（優先順）
JOB_SELECTORS = [
    "a[href*='/work/detail/']",
    ".c-media__heading a",
    ".c-jobListItem__title a", 
    ".p-jobList__item a",
    "[data-testid='job-title'] a",
    ".job-title a"
]

PRICE_SELECTORS = [
    ".c-media__price",
    ".price", 
    ".budget",
    ".c-jobListItem__price"
]

# ユーザーエージェント
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# フィルタリング設定
MIN_PRICE_FILTER = 0  # 最低価格フィルタ（円）
EXCLUDE_KEYWORDS = ["テスト", "練習"]  # 除外キーワード