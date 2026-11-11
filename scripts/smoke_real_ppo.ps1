param(
    [ValidateSet('no_pest', 'experimental_pest')][string]$Mode = 'no_pest',
    [switch]$LegacyMetadata
)
$ErrorActionPreference = 'Stop'
# Use immutable run folders and corrected metadata by default.
& (Join-Path $PSScriptRoot 'benchmark_real_ppo.ps1') -Device cpu -Mode $Mode -Steps 1024 -LegacyMetadata:$LegacyMetadata
