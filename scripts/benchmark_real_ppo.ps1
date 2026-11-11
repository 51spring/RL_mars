param(
    [ValidateSet('cpu','cuda')][string]$Device = 'cpu',
    [ValidateSet('no_pest','experimental_pest')][string]$Mode = 'experimental_pest',
    [int]$Steps = 102400,
    [ValidateSet('enabled','disabled')][string]$DistributionValidation = 'enabled',
    [switch]$LegacyMetadata,
    [string]$Resume = ''
)
$ErrorActionPreference = 'Stop'
$workspacePath = (Resolve-Path -LiteralPath (Split-Path $PSScriptRoot -Parent)).Path
Set-Location -LiteralPath $workspacePath
$image = if ($Device -eq 'cuda') { 'mars-dssat:ppo-cuda' } else { 'mars-dssat:ppo-cpu' }
if (-not $LegacyMetadata) { $image += '-metadata' }
$imageId = & docker image inspect $image --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { throw "Build $image first" }
$dockerArgs = @('run','--rm','--cpus','4','--memory','6g','--env',"MARS_IMAGE_ID=$imageId",'--entrypoint','/usr/bin/timeout','--mount',"type=bind,source=$workspacePath,target=/workspace")
if ($Device -eq 'cuda') { $dockerArgs += @('--gpus','all') }
$dockerArgs += @($image,'--kill-after=10s','3600s','/opt/mars_ppo/bin/python','/workspace/scripts/benchmark_real_ppo.py','--steps',"$Steps",'--mode',$Mode,'--device',$Device,'--distribution-validation',$DistributionValidation,'--image-id',$imageId)
if ($Resume) {
    $resumePath = (Resolve-Path -LiteralPath $Resume).Path
    if (-not $resumePath.StartsWith($workspacePath + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Resume must be within this project' }
    $relative = $resumePath.Substring($workspacePath.Length).Replace('\','/')
    $dockerArgs += @('--resume',"/workspace$relative")
}
& docker @dockerArgs
if ($LASTEXITCODE -ne 0) { throw 'Benchmark failed; inspect new outputs/runs failure.json' }
