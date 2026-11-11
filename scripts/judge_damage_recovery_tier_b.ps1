$ErrorActionPreference='Stop'
$workspacePath=(Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
$image='mars-dssat:ppo-cpu-metadata'
$imageId=& docker image inspect $image --format '{{.Id}}'
if($LASTEXITCODE -ne 0){throw 'Corrected PPO image is unavailable'}
& docker run --rm --cpus 4 --memory 4g --env "MARS_IMAGE_ID=$imageId" --entrypoint /usr/bin/timeout --mount "type=bind,source=$workspacePath,target=/workspace" $image --kill-after=10s 5400s /opt/gym_dssat_pdi/bin/python /workspace/scripts/judge_damage_recovery_tier_b.py
if($LASTEXITCODE -ne 0){throw 'Tier B comparison failed; inspect the unique run folder'}
