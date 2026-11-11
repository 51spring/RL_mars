$ErrorActionPreference = 'Stop'
$workspacePath = (Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
Set-Location -LiteralPath $workspacePath
& docker build -f docker/Dockerfile.metadata -t mars-dssat:metadata-audit .
if ($LASTEXITCODE -ne 0) { throw 'Metadata/harvest audit image build failed' }
$imageId = & docker image inspect mars-dssat:metadata-audit --format '{{.Id}}'
& docker run --rm --cpus 4 --memory 4g --env "MARS_IMAGE_ID=$imageId" --entrypoint /usr/bin/timeout --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:metadata-audit --kill-after=10s 600s /opt/gym_dssat_pdi/bin/python /workspace/scripts/verify_metadata_harvest.py --image-id $imageId
if ($LASTEXITCODE -ne 0) { throw 'Metadata/harvest audit failed; inspect new outputs/runs directory' }
