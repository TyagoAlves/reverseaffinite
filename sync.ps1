# reverseaffinite Windows Sync Script
param(
    [string]$RepoPath = "C:\reverseaffinite"
)

Write-Host "=== reverseaffinite Windows Sync ===" -ForegroundColor Cyan

Write-Host "1) Pull latest from GitHub" -ForegroundColor Yellow
if (-not (Test-Path $RepoPath)) {
    git clone --recursive https://github.com/TyagoAlves/reverseaffinite.git $RepoPath
}
git -C $RepoPath pull origin main 2>&1 | ForEach-Object { Write-Host $_ }

Write-Host "2) Build C++ engine for Windows" -ForegroundColor Yellow
& "$RepoPath\cpp_editor\build_windows.ps1"

if ($LASTEXITCODE -eq 0) {
    Write-Host "=== Windows Build Complete ===" -ForegroundColor Green
}
