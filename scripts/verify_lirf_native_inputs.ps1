$ErrorActionPreference='Stop'
$workspacePath=(Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
$expected='sha256:a799dff2bf7f393e463b23fb9f8e2f6d33fc08d575a6fa6db26291690c904f98'
$imageId=(& docker image inspect mars-dssat:actual-harvest-candidate --format '{{.Id}}').Trim()
if($LASTEXITCODE -ne 0 -or $imageId -ne $expected){throw 'Qualified native diagnostic image required'}
& docker run --rm --user 0 --cpus 4 --memory 4g --env "MARS_IMAGE_ID=$imageId" --entrypoint /usr/bin/timeout --mount "type=bind,source=$workspacePath,target=/workspace" $imageId --kill-after=10s 240s /opt/gym_dssat_pdi/bin/python /workspace/scripts/verify_lirf_native_inputs.py
if($LASTEXITCODE -ne 0){throw 'Native diagnostic runner failed; inspect retained run outputs'}
