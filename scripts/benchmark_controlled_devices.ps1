param([ValidateSet(1024,102400)][int]$Steps=1024)
$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
$running = & docker ps --quiet
if ($LASTEXITCODE -ne 0) { throw 'Docker engine unavailable' }
if ($running) { throw 'Stop other container workloads before a controlled measurement' }
$imageId = & docker image inspect 'mars-dssat:ppo-cuda-metadata' --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { throw 'Metadata-corrected CUDA image unavailable' }
& docker run --rm --gpus all --cpus 4 --memory 6g --env "MARS_IMAGE_ID=$imageId" --mount "type=bind,source=$workspace,target=/workspace" --entrypoint /usr/bin/timeout $imageId --kill-after=10s 10800s /opt/mars_ppo/bin/python /workspace/scripts/benchmark_controlled_devices.py --steps $Steps
if ($LASTEXITCODE -ne 0) { throw 'Controlled device benchmark failed' }
