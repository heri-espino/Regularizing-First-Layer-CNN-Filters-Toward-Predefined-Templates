param(
    [string]$InputRoot = "results/retention_release_001",
    [string]$OutputRoot = "analysis/kernel_similarity/results",
    [string]$Python = "python"
)
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
& $Python -c "import torch, numpy, scipy, pandas, matplotlib, PIL"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Activate your experiment environment or run:"
    Write-Host "$Python -m pip install -r analysis/kernel_similarity/requirements.txt"
    exit 1
}
& $Python analysis/kernel_similarity/analyze.py --input $InputRoot --output $OutputRoot
exit $LASTEXITCODE
