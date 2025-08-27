param([switch]$Force)

Set-Location "C:\Users\SUZUKI Natsumi\lancers-teams-notifier"

# Git（PATHが無い環境用にフルパス候補も用意）
$Git = "git"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  $Git = "C:\Program Files\Git\bin\git.exe"
}

& $Git fetch origin main | Out-Null
$local  = & $Git rev-parse HEAD
$remote = & $Git rev-parse origin/main

if ($Force -or ($local -ne $remote)) {
  if (-not $Force) { & $Git pull origin main | Out-Null }

  $src = Join-Path $PWD "案件情報.xlsx"
  $dst = "C:\Users\SUZUKI Natsumi\株式会社ReySolid\【B】IT-Solution@ReySolid - 案件管理 - ドキュメント\案件管理\案件情報.xlsx"

  if (Test-Path $src) {
    try {
      Copy-Item $src $dst -Force
      Write-Host "✅ Excel同期: $(Get-Date)  $dst"
    } catch {
      Write-Host " コピー失敗: $($_.Exception.Message)"
    }
  } else {
    Write-Host "ℹ Excel未生成（まだGitHub Actionsが出力していない可能性）"
  }
} else {
  Write-Host " 更新なし: $(Get-Date)"
}
