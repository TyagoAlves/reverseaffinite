param([switch]$Run)
Write-Host "=== reverseaffinity Photo Editor - Windows Setup ===" -ForegroundColor Cyan
Write-Host ""
$ErrorActionPreference = "Stop"

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[1/4] Baixando Python..." -ForegroundColor Yellow
    $url = "https://www.python.org/ftp/python/3.12.5/python-3.12.5-amd64.exe"
    $out = "$env:TEMP\python-installer.exe"
    Invoke-WebRequest -Uri $url -OutFile $out
    Write-Host "[2/4] Instalando Python..." -ForegroundColor Yellow
    Start-Process -Wait -FilePath $out -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1"
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

Write-Host "[3/4] Instalando dependencias..." -ForegroundColor Yellow
python -m pip install --upgrade pip -q
python -m pip install PyQt5 numpy -q

Write-Host "[4/4] Baixando reverseaffinity..." -ForegroundColor Yellow
$zipUrl = "https://github.com/TyagoAlves/reverseaffinity/archive/refs/heads/main.zip"
$zipOut = "$env:TEMP\reverseaffinity.zip"
Invoke-WebRequest -Uri $zipUrl -OutFile $zipOut
Expand-Archive -Path $zipOut -DestinationPath "$env:USERPROFILE\reverseaffinity" -Force

$appDir = "$env:USERPROFILE\reverseaffinity\reverseaffinity-main"
Write-Host ""
Write-Host "=== Pronto! ===" -ForegroundColor Green
Write-Host "Para iniciar o editor, execute:" -ForegroundColor White
Write-Host "   cd $appDir" -ForegroundColor Cyan
Write-Host "   python main.py" -ForegroundColor Cyan
Write-Host ""

if ($Run) {
    Write-Host "Iniciando editor..." -ForegroundColor Yellow
    Set-Location $appDir
    python main.py
}
