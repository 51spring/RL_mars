# Entropy-bonus experiment for decision_project.md section 25 (hypothesis H): seeds 0 and 2, ent_coef 0.01,
# otherwise the current configuration. Run one after another (Docker has 8 GB in total).
$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$image = 'mars-dssat:ppo-cpu-metadata'
$imageId = (& docker image inspect $image --format '{{.Id}}').Trim()
$common = @('--steps', '1024000', '--chunk', '51200', '--n-envs', '8', '--gae-lambda', '0.95', '--ent-coef', '0.01')
foreach ($fit in 'b1_s0', 'b1_s2') {
    Write-Output "START $fit $(Get-Date -Format 'HH:mm')"
    $argv = @('run', '--rm', '--cpus', '12', '--memory', '7g', '--env', "MARS_IMAGE_ID=$imageId",
              '--entrypoint', '/usr/bin/timeout', '--mount', "type=bind,source=$workspace,target=/workspace",
              $image, '--kill-after=10s', '14400s', '/opt/mars_ppo/bin/python', '/workspace/scripts/pilot_learning_curve.py',
              '--fit', $fit) + $common
    & docker @argv 2>&1 | Select-String -Pattern 'RUN_DIR|CHECKPOINT|Error|Traceback' | ForEach-Object { "$fit $($_.Line)" }
    Write-Output "END $fit exit=$LASTEXITCODE $(Get-Date -Format 'HH:mm')"
}
