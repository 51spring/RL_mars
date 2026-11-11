param([ValidateRange(1,16)][int]$Seasons=4)
$ErrorActionPreference='Stop'
$workspacePath=(Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
$image='mars-dssat:ppo-cpu-metadata'
$imageId=& docker image inspect $image --format '{{.Id}}'
if($LASTEXITCODE -ne 0){throw 'Corrected PPO image is unavailable'}
& docker run --rm --cpus 4 --memory 4g --env "MARS_IMAGE_ID=$imageId" --entrypoint /usr/bin/timeout --mount "type=bind,source=$workspacePath,target=/workspace" $image --kill-after=10s 600s /opt/mars_ppo/bin/python /workspace/scripts/evaluate_baseline_pairs.py --seasons $Seasons
if($LASTEXITCODE -ne 0){throw 'Baseline pair diagnostic failed; inspect the unique run folder'}
