param([string]$Evidence='outputs/runs/20261106T070340Z_actual_harvest_domain_3ef3f2a6')
$ErrorActionPreference='Stop'
$workspacePath=(Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
$sourcePath=(Resolve-Path -LiteralPath (Join-Path $workspacePath $Evidence)).Path
if(-not $sourcePath.StartsWith($workspacePath+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Evidence must be inside this project'}
$relative=$sourcePath.Substring($workspacePath.Length).Replace('\','/')
$image='mars-dssat:actual-harvest-candidate'
$imageId=& docker image inspect $image --format '{{.Id}}'
if($LASTEXITCODE -ne 0 -or $imageId -ne 'sha256:a799dff2bf7f393e463b23fb9f8e2f6d33fc08d575a6fa6db26291690c904f98'){throw 'Expected preserved candidate image'}
& docker run --rm --cpus 4 --memory 4g --env "MARS_IMAGE_ID=$imageId" --entrypoint /usr/bin/timeout --mount "type=bind,source=$workspacePath,target=/workspace" $image --kill-after=10s 120s /opt/gym_dssat_pdi/bin/python /workspace/scripts/audit_carbon_measurement.py "/workspace$relative"
if($LASTEXITCODE -ne 0){throw 'Carbon source/output audit failed; inspect the new run folder'}
