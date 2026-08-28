$ErrorActionPreference = "Stop"

Write-Host "[1/4] Python preflight..."
$pythonExe = "C:\Users\wmwm1\OneDrive\Desktop\work\.venv\Scripts\python.exe"
$pyFiles = @(
    "discord_bot.py",
    "save_backend.py",
    "pet.py",
    "shop.py",
    "adventure.py",
    "species.py",
    "storage.py",
    "achievements.py",
    "main.py"
)

if (-not (Test-Path -LiteralPath $pythonExe)) {
    Write-Error "지정 Python 실행 파일을 찾지 못했습니다: $pythonExe"
    exit 1
}

$missing = $pyFiles | Where-Object { -not (Test-Path -LiteralPath $_) }
if ($missing) {
    Write-Error "필수 검증 파일이 없습니다: $($missing -join ', ')"
    exit 1
}

& $pythonExe -m py_compile @pyFiles
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python 문법 검증 실패. 배포를 중단합니다."
    exit $LASTEXITCODE
}
Write-Host "OK: Python syntax"

Write-Host "[2/4] Git status..."
$changes = git status --porcelain
if (-not $changes) {
    Write-Host "변경사항 없음. 배포하지 않습니다."
    exit 0
}

git status --short

Write-Host "[3/4] Commit..."
git add .
git commit -m "Auto deploy update"
if ($LASTEXITCODE -ne 0) {
    Write-Error "git commit 실패."
    exit $LASTEXITCODE
}

Write-Host "[4/4] Push -> Render Auto Deploy..."
git push
if ($LASTEXITCODE -ne 0) {
    Write-Error "git push 실패. Render 배포는 시작되지 않았습니다."
    exit $LASTEXITCODE
}

Write-Host "완료: GitHub push 성공. Render Auto-Deploy가 시작됩니다."
