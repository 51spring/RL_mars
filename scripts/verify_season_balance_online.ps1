$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$workspacePath = (Get-Location).Path
& docker run --rm --cpus 4 --memory 4g --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:leaf-experimental 'timeout --kill-after=5s 120s python /workspace/scripts/verify_season_balance_online.py'
if ($LASTEXITCODE -ne 0) { throw 'Season balance / online diagnostic verification failed' }
