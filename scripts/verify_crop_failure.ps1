$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$workspacePath = (Get-Location).Path
& docker run --rm --cpus 4 --memory 4g --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:integration 'python /workspace/scripts/verify_crop_failure.py'
if ($LASTEXITCODE -ne 0) { throw 'Actual DSSAT crop-failure validation failed' }
