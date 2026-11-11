$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$workspacePath = (Get-Location).Path
& docker run --rm --cpus 4 --memory 4g --mount "type=bind,source=$workspacePath,target=/workspace" gym-dssat:debian-bookworm 'python /workspace/scripts/verify_dssat_backend.py'
if ($LASTEXITCODE -ne 0) { throw 'DSSAT terminal bridge regression failed' }
