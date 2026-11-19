param(
    [ValidateSet('Check', 'Smoke', 'B3Threshold', 'B3Weekly', 'B1Entropy', 'Train', 'FinalEvaluate')]
    [string] $Mode = 'Check',
    [switch] $LoadImage,
    [string] $ImageArchive,
    [switch] $Quick,
    [string] $RunFolder
)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$image = 'sha256:11e2650fed7582c23badafd3c064711679a6b92c9e8d6969a3936c452131567e'
if ($Quick -and $Mode -notin @('B3Weekly', 'B1Entropy')) {
    throw '-Quick is supported by B3Weekly and B1Entropy.'
}
if ($Mode -eq 'FinalEvaluate' -and -not $RunFolder) {
    throw 'FinalEvaluate requires -RunFolder pointing to a completed main-training run.'
}
if ($RunFolder -and $Mode -notin @('Train','FinalEvaluate')) {
    throw '-RunFolder is supported by Train and FinalEvaluate.'
}
if ($ImageArchive -and !$LoadImage) {
    throw '-ImageArchive requires -LoadImage.'
}
if ($LoadImage) {
    if (!$ImageArchive) {
        $ImageArchive = Join-Path $root 'runtime/mars-dssat-ppo-cpu-metadata.tar'
    }
    $archive = (Resolve-Path -LiteralPath $ImageArchive).Path
    docker load --input $archive
    if ($LASTEXITCODE -ne 0) { throw 'Docker image load failed.' }
}
$actual = docker image inspect $image --format '{{.Id}} {{.Os}}/{{.Architecture}}'
if ($LASTEXITCODE -ne 0 -or $actual -ne "$image linux/amd64") {
    throw 'The required Linux amd64 image is missing. Start Docker and use -LoadImage.'
}
$mounts = @()
$pythonArgs = @()
$output = Join-Path $root 'outputs/runs'
if ($Mode -eq 'FinalEvaluate' -or ($Mode -eq 'Train' -and $RunFolder)) {
    $run = (Resolve-Path -LiteralPath $RunFolder).Path
    if ($Mode -eq 'FinalEvaluate' -and !(Test-Path -LiteralPath (Join-Path $run 'training_complete.json') -PathType Leaf)) {
        throw 'Main training is incomplete. No final evaluation was started.'
    }
    if (!(Test-Path -LiteralPath (Join-Path $run 'source_snapshot/scripts/run_comparison.py') -PathType Leaf)) {
        throw 'The run is missing its frozen source snapshot.'
    }
    $output = if ($Mode -eq 'FinalEvaluate') { Join-Path $run 'report_test' } else { $run }
    $mounts += @('--mount', "type=bind,source=$run,target=/workspace")
    $pythonArgs = @('/workspace/source_snapshot/scripts/run_comparison.py','--resume','/workspace')
    if ($Mode -eq 'FinalEvaluate') {
        $pythonArgs += @('--phase','evaluate','--evaluation-split','test')
    } else {
        $pythonArgs += @('--phase','train')
    }
} elseif ($Mode -eq 'Train') {
    $mounts += @('--mount', "type=bind,source=$root,target=/workspace")
    $pythonArgs = @('/workspace/scripts/run_comparison.py','--phase','train')
} elseif ($Mode -in @('Check','Smoke')) {
    $mounts += @('--mount', "type=bind,source=$root,target=/workspace")
    if ($Mode -eq 'Check') {
        $pythonArgs = @('-m','unittest',
            'tests/test_baseline_evaluation.py','tests/test_comparison.py','tests/test_economics.py',
            'tests/test_environment.py','tests/test_exogenous_pests.py','tests/test_protocol.py',
            'tests/test_resources.py','tests/test_rewards.py')
    } else {
        $pythonArgs = @('/workspace/scripts/verify_final_pipeline.py')
    }
} else {
    $target = switch ($Mode) {
        'B3Threshold' { 'b3_threshold_100k' }
        'B3Weekly' { 'b3_weekly_threshold_100k' }
        'B1Entropy' { 'b1_entropy_0p001_100k' }
    }
    $runner = if ($Mode -eq 'B3Weekly') { 'run_weekly.py' } else { 'run.py' }
    $stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ') + '_' + [Guid]::NewGuid().ToString('N').Substring(0,8)
    $output = Join-Path $root "outputs/replays/${target}_$stamp"
    New-Item -ItemType Directory -Path $output | Out-Null
    Copy-Item -LiteralPath (Join-Path $root "outputs/$target/$runner") -Destination (Join-Path $output $runner)
    $history = Join-Path $root 'historical_source'
    $mounts += @('--mount', "type=bind,source=$history,target=/workspace,readonly",
        '--mount', "type=bind,source=$root,target=/workdocs,readonly",
        '--mount', "type=bind,source=$output,target=/workdocs/outputs/$target")
    $pythonArgs = @("/workdocs/outputs/$target/$runner")
    if ($Quick) { $pythonArgs += $(if ($Mode -eq 'B3Weekly') { '--smoke' } else { '--check' }) }
}
$dockerArgs = @('run','--rm','--platform','linux/amd64','--cpus','8','--memory','7g',
    '--env',"MARS_IMAGE_ID=$image",'--env','PYTHONPATH=/workspace/src:/workspace/tests',
    '--env','PYTHONDONTWRITEBYTECODE=1','--workdir','/workspace',
    '--entrypoint','/opt/mars_ppo/bin/python') + $mounts + @($image,'-u') + $pythonArgs
Write-Host "Mode $Mode. Output location: $output"
docker @dockerArgs
if ($LASTEXITCODE -ne 0) { throw "Docker experiment failed with exit code $LASTEXITCODE." }
