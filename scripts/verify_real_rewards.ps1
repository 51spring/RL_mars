$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$workspacePath = (Get-Location).Path
& docker run --rm --cpus 4 --memory 4g --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:leaf-experimental 'timeout --kill-after=5s 90s python /workspace/scripts/verify_real_rewards.py'
if ($LASTEXITCODE -ne 0) { throw 'Real DSSAT potential reward verification failed' }
