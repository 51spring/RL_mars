$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$workspacePath = (Get-Location).Path
$image = 'mars-dssat:actual-harvest-candidate'
$imageId = (& docker image inspect $image --format '{{.Id}}').Trim()
if ($LASTEXITCODE -ne 0 -or $imageId -ne 'sha256:a799dff2bf7f393e463b23fb9f8e2f6d33fc08d575a6fa6db26291690c904f98') {
    throw 'Diagnostic requires the qualified actual-harvest candidate image'
}
& docker run --rm --user 0 --cpus 4 --memory 4g --mount "type=bind,source=$workspacePath,target=/workspace" --env "MARS_IMAGE_ID=$imageId" --entrypoint /opt/gym_dssat_pdi/bin/python $imageId /workspace/scripts/verify_germination_failure.py
if ($LASTEXITCODE -ne 0) { throw 'Native dry germination diagnostic failed' }
