$ErrorActionPreference = 'Stop'
$workspacePath = (Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
Set-Location -LiteralPath $workspacePath
$imageId = & docker image inspect mars-dssat:leaf-experimental --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { throw 'Build mars-dssat:leaf-experimental first' }
& docker run --rm --cpus 4 --memory 4g --entrypoint /usr/bin/timeout --mount "type=bind,source=$workspacePath,target=/workspace" mars-dssat:leaf-experimental --kill-after=10s 180s /opt/gym_dssat_pdi/bin/python /workspace/scripts/audit_model_contract.py --image-id $imageId
if ($LASTEXITCODE -ne 0) { throw 'Native model contract audit failed; inspect new outputs/runs failure.json' }
