$ErrorActionPreference='Stop'
$workspacePath=(Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
$image='mars-dssat:actual-harvest-candidate'
$imageId=& docker image inspect $image --format '{{.Id}}'
if($LASTEXITCODE -ne 0){throw 'Existing candidate image is required'}
if($imageId -ne 'sha256:a799dff2bf7f393e463b23fb9f8e2f6d33fc08d575a6fa6db26291690c904f98'){throw 'Candidate image identity changed; audit required'}
& docker run --rm --cpus 4 --memory 4g --env "MARS_IMAGE_ID=$imageId" --entrypoint /usr/bin/timeout --mount "type=bind,source=$workspacePath,target=/workspace" $image --kill-after=10s 600s /opt/gym_dssat_pdi/bin/python /workspace/scripts/verify_actual_harvest_domain.py
if($LASTEXITCODE -ne 0){throw 'Domain audit failed; retained evidence must be inspected'}
