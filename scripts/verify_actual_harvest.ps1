$ErrorActionPreference = 'Stop'
$workspacePath = (Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
Set-Location -LiteralPath $workspacePath
& docker build -f docker/Dockerfile.ear-audit -t mars-dssat:ear-audit .
if ($LASTEXITCODE -ne 0) { throw 'Ear audit build failed; harvest-n-candidate base required' }
& docker build -f docker/Dockerfile.actual-harvest -t mars-dssat:actual-harvest-candidate .
if ($LASTEXITCODE -ne 0) { throw 'Actual harvest candidate build failed' }
$imageId = & docker image inspect mars-dssat:actual-harvest-candidate --format '{{.Id}}'
& docker run --rm --cpus 4 --memory 4g --env "MARS_IMAGE_ID=$imageId" --entrypoint /usr/bin/timeout --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:actual-harvest-candidate --kill-after=10s 600s /opt/gym_dssat_pdi/bin/python /workspace/scripts/verify_actual_harvest.py
if ($LASTEXITCODE -ne 0) { throw 'Actual harvest contract audit failed' }
& docker run --rm --env "MARS_IMAGE_ID=$imageId" --entrypoint /opt/gym_dssat_pdi/bin/python --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:actual-harvest-candidate /workspace/scripts/audit_actual_harvest_source.py
if ($LASTEXITCODE -ne 0) { throw 'Source fingerprint verification failed' }
