$ErrorActionPreference = 'Stop'
$workspacePath = (Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
Set-Location -LiteralPath $workspacePath
& docker build -f docker/Dockerfile.sequence -t mars-dssat:sequence-native .
if ($LASTEXITCODE -ne 0) { throw 'Native sequence image build failed' }
$imageId = & docker image inspect mars-dssat:sequence-native --format '{{.Id}}'
& docker run --rm --cpus 4 --memory 4g --env "MARS_IMAGE_ID=$imageId" --entrypoint /usr/bin/timeout --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:sequence-native --kill-after=10s 300s /opt/gym_dssat_pdi/bin/python /workspace/scripts/verify_c_harvest_accounting.py
if ($LASTEXITCODE -ne 0) { throw 'C harvest accounting failed; inspect new outputs/runs directory' }
