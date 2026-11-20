param(
    [string]$Python = 'python',
    [switch]$CpuOnly
)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force -Path tmp, outputs | Out-Null
$env:TEMP = Join-Path (Get-Location) 'tmp'
$env:TMP = $env:TEMP
if (-not (Test-Path '.venv/Scripts/python.exe')) {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'venv creation failed' }
}
$venvPython = Join-Path (Get-Location) '.venv/Scripts/python.exe'
& $venvPython -m ensurepip --upgrade
if ($LASTEXITCODE -ne 0) { throw 'pip bootstrap failed' }
& $venvPython -m pip install --upgrade pip --cache-dir .cache/pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed' }
$torchIndex = if ($CpuOnly) { 'https://download.pytorch.org/whl/cpu' } else { 'https://download.pytorch.org/whl/cu118' }
& $venvPython -m pip install 'torch==2.5.1' --no-deps --index-url $torchIndex --cache-dir .cache/pip
if ($LASTEXITCODE -ne 0) { throw 'PyTorch install failed' }
& $venvPython -m pip install -e . --cache-dir .cache/pip
if ($LASTEXITCODE -ne 0) { throw 'Project install failed' }
& $venvPython scripts/check_environment.py
if ($LASTEXITCODE -ne 0) { throw 'Environment check failed' }
& $venvPython scripts/smoke_ppo.py --device cpu
if ($LASTEXITCODE -ne 0) { throw 'PPO interface check failed' }
