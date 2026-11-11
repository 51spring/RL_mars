$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$workspacePath = (Get-Location).Path
& docker run --rm --cpus 4 --memory 4g --mount "type=bind,source=$workspacePath,target=/workspace" gym-dssat:debian-bookworm 'python /workspace/scripts/probe_dssat_contract.py'
if ($LASTEXITCODE -ne 0) { throw 'DSSAT contract probe failed; inspect outputs/dssat_contract_probe.json' }
