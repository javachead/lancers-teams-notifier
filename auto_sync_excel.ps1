# auto_sync_excel.ps1
$ErrorActionPreference = "Continue"

$repoPath = "C:\Users\SUZUKI Natsumi\lancers-teams-notifier"
$sharePointPath = "C:\Users\SUZUKI Natsumi\株式会社ReySolid\【B】IT-Solution@ReySolid - 案件管理 - ドキュメント\案件管理\案件情報.xlsx"
$logFile = "$repoPath\sync_log.txt"

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content $logFile "[$timestamp] 同期開始"

Set-Location $repoPath

git reset --hard origin/main 2>&1 | Out-Null
git pull origin main 2>&1 | Out-Null

if (Test-Path "案件情報.xlsx") {
    Copy-Item "案件情報.xlsx" $sharePointPath -Force
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content $logFile "[$timestamp]  同期成功"
    Write-Host " 同期完了: $timestamp" -ForegroundColor Green
} else {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content $logFile "[$timestamp]  ファイルなし"
    Write-Host " ファイルが見つかりません" -ForegroundColor Red
}
