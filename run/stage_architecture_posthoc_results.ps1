param(
    [string]$SourceRoot = $(if ($env:ARCH_POSTHOC_ROOT) {
        $env:ARCH_POSTHOC_ROOT
    } else {
        Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\architecture_posthoc_diagnostics_001'
    }),
    [string]$DestinationPrefix = 'analysis/architecture_posthoc_diagnostics_001'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $RepoRoot
try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'git is required.' }
    $SourceRoot = (Resolve-Path $SourceRoot).Path

    foreach ($required in @('REPORT.md','execution_manifest.json','omnibus_robustness.csv','selected_random_summary.csv','alignment_B_architecture_summary.csv','architecture_definitions.csv')) {
        $path = Join-Path $SourceRoot $required
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Missing post hoc diagnostic artifact: $path"
        }
    }

    $files = Get-ChildItem -LiteralPath $SourceRoot -File | ForEach-Object {
        [pscustomobject]@{
            Source = $_.FullName
            Destination = "$DestinationPrefix/$($_.Name)"
        }
    }

    foreach ($file in ($files | Sort-Object Destination -Unique)) {
        $blob = (& git hash-object -w -- $file.Source).Trim()
        if ($LASTEXITCODE -ne 0 -or -not $blob) { throw "git hash-object failed: $($file.Source)" }
        & git update-index --add --cacheinfo 100644 $blob $file.Destination
        if ($LASTEXITCODE -ne 0) { throw "git update-index failed: $($file.Destination)" }
        & git update-index --skip-worktree -- $file.Destination
        if ($LASTEXITCODE -ne 0) { throw "Could not mark skip-worktree: $($file.Destination)" }
        Write-Host "STAGED $($file.Destination)"
    }

    Write-Host ''
    Write-Host 'Post hoc architecture diagnostic results are staged directly in Git.'
    Write-Host 'Review with: git diff --cached --stat'
}
finally {
    Pop-Location
}
