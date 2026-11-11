$ErrorActionPreference = 'Stop'
$workspacePath = (Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
Set-Location -LiteralPath $workspacePath
$imageId = & docker image inspect mars-dssat:harvest-n-candidate --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { throw 'Build harvest-n-candidate before this diagnostic' }
& docker run --rm --cpus 4 --memory 4g --env "MARS_IMAGE_ID=$imageId" --entrypoint /usr/bin/timeout --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:harvest-n-candidate --kill-after=10s 600s /opt/gym_dssat_pdi/bin/python /workspace/scripts/verify_harvest_n_scope.py
if ($LASTEXITCODE -ne 0) { throw 'Scope audit failed to complete; inspect new outputs/runs directory' }
