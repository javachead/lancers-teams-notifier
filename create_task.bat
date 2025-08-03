@echo off
chcp 65001 >nul
echo ======================================
echo Playwright修正とテスト実行
echo ======================================

REM 現在のディレクトリに移動
cd /d "C:\Users\SUZUKI Natsumi\lancers-teams-notifier"

echo 仮想環境をアクティベート中...
call .venv\Scripts\activate.bat

echo.
echo ======================================
echo Playwrightブラウザをインストール中...
echo ======================================
playwright install

if %errorlevel% equ 0 (
    echo ✅ Playwrightブラウザのインストール完了
) else (
    echo ❌ Playwrightブラウザのインストール失敗
    pause
    exit /b 1
)

echo.
echo ======================================
echo スクリプトのテスト実行
echo ======================================
echo fetch_lancers_advanced.py をテスト実行中...

python fetch_lancers_advanced.py

echo.
echo ======================================
echo 実行完了
echo ======================================

echo 既存のタスクの状態確認:
schtasks /query /tn "LancersWeeklyNotifier"

echo.
echo ======================================
echo すべて完了！
echo 毎週火曜日16:00に自動実行されます
echo ======================================

pause