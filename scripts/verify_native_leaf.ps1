$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$workspacePath = (Get-Location).Path
& docker run --rm --cpus 4 --memory 4g --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:leaf-experimental 'timeout --kill-after=5s 90s python /workspace/scripts/verify_native_leaf.py'
if ($LASTEXITCODE -ne 0) { throw 'Native leaf-write verification failed' }
& docker image inspect mars-dssat:leaf-experimental --format '{{.Id}}' | Set-Content -Encoding utf8 outputs/native-leaf-image-id.txt
