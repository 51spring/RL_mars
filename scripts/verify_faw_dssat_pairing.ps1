$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
$image = 'mars-dssat:ppo-cpu-metadata'
$imageId = & docker image inspect $image --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { throw "Docker image unavailable: $image" }
& docker run --rm --cpus 4 --memory 4g --env "MARS_IMAGE_ID=$imageId" --mount "type=bind,source=$workspace,target=/workspace" --entrypoint /usr/bin/timeout $image --kill-after=5s 180s /opt/mars_ppo/bin/python /workspace/scripts/verify_faw_dssat_pairing.py
if ($LASTEXITCODE -ne 0) { throw 'DSSAT pest sensitivity pairing failed' }
