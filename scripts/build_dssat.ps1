$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
& docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Docker Linux engine is unavailable. See docs/SETUP.md.' }
# Official upstream recipe. It uses legacy Gym and a separate Linux Python env.
# Keep it separate from the modern Gymnasium/SB3 host development environment.
& docker build vendor/gym_dssat_pdi/docker_recipes -t gym-dssat:debian-bookworm -f vendor/gym_dssat_pdi/docker_recipes/Dockerfile_Debian_Bookworm
if ($LASTEXITCODE -ne 0) { throw 'Upstream DSSAT image build failed' }
& docker image inspect gym-dssat:debian-bookworm --format '{{.Id}}' | Set-Content -Encoding utf8 outputs/dssat-image-id.txt
& docker run --rm --cpus 4 --memory 4g gym-dssat:debian-bookworm
if ($LASTEXITCODE -ne 0) { throw 'Upstream DSSAT example failed' }
