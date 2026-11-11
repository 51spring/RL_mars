$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
& docker build -f docker/Dockerfile.integration -t mars-dssat:integration .
if ($LASTEXITCODE -ne 0) { throw 'Gymnasium integration image build failed' }
$workspacePath = (Get-Location).Path
& docker run --rm --cpus 4 --memory 4g --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:integration 'python /workspace/scripts/verify_gym_integration.py'
if ($LASTEXITCODE -ne 0) { throw 'Real DSSAT Gymnasium integration regression failed' }
& docker image inspect mars-dssat:integration --format '{{.Id}}' | Set-Content -Encoding utf8 outputs/dssat-integration-image-id.txt
