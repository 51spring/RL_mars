$ErrorActionPreference = 'Stop'
$workspacePath = (Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
Set-Location -LiteralPath $workspacePath
& docker build -f docker/Dockerfile.harvest-n -t mars-dssat:harvest-n-candidate .
if ($LASTEXITCODE -ne 0) { throw 'Harvest N candidate build failed; build sequence-native base first' }
$imageId = & docker image inspect mars-dssat:harvest-n-candidate --format '{{.Id}}'
& docker run --rm --cpus 4 --memory 4g --env "MARS_IMAGE_ID=$imageId" --entrypoint /usr/bin/timeout --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:harvest-n-candidate --kill-after=10s 600s /opt/gym_dssat_pdi/bin/python /workspace/scripts/verify_harvest_n_candidate.py
if ($LASTEXITCODE -ne 0) { throw 'Harvest N candidate validation failed; inspect new outputs/runs directory' }
