# Separation experiments for decision_project.md section 25, run one after another (Docker has 8 GB in total;
# four parallel runs with 4 GB each timed out on 2026-11-12). Each run: 1,024,000 steps, current config.
$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$image = 'mars-dssat:ppo-cpu-metadata'
$imageId = (& docker image inspect $image --format '{{.Id}}').Trim()
$common = @('--steps', '1024000', '--chunk', '51200', '--n-envs', '8', '--gae-lambda', '0.95')
$runs = [ordered]@{
    'lrlinear'  = @('--fit', 'b1_s0', '--lr-schedule', 'linear')
    'noshaping' = @('--fit', 'b1_s0', '--no-shaping')
    'seed1'     = @('--fit', 'b1_s1')
    'seed2'     = @('--fit', 'b1_s2')
}
foreach ($name in $runs.Keys) {
    Write-Output "START $name $(Get-Date -Format 'HH:mm')"
    $argv = @('run', '--rm', '--cpus', '12', '--memory', '7g', '--env', "MARS_IMAGE_ID=$imageId",
              '--entrypoint', '/usr/bin/timeout', '--mount', "type=bind,source=$workspace,target=/workspace",
              $image, '--kill-after=10s', '14400s', '/opt/mars_ppo/bin/python', '/workspace/scripts/pilot_learning_curve.py') +
            $common + $runs[$name]
    & docker @argv 2>&1 | Select-String -Pattern 'RUN_DIR|CHECKPOINT|Error|Traceback' | ForEach-Object { "$name $($_.Line)" }
    Write-Output "END $name exit=$LASTEXITCODE $(Get-Date -Format 'HH:mm')"
}
