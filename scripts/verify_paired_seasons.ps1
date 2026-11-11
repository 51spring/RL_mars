$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
& .\.venv\Scripts\python.exe scripts/generate_season_manifest.py
if ($LASTEXITCODE -ne 0) { throw 'Season manifest generation failed' }
$workspacePath = (Get-Location).Path
& docker run --rm --cpus 4 --memory 4g --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:integration 'python /workspace/scripts/verify_paired_seasons.py'
if ($LASTEXITCODE -ne 0) { throw 'Paired actual DSSAT seasons failed verification' }
