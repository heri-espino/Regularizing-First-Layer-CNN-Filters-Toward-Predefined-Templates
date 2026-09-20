param(
    [string]$SourceRoot = $(if ($env:STAGE_F_ROOT) {
        $env:STAGE_F_ROOT
    } else {
        Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\architecture_robustness_cuda_001'
    }),
    [string]$DestinationPrefix = 'analysis/architecture_robustness_001'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $RepoRoot
try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw 'git is required.'
    }

    $SourceRoot = (Resolve-Path $SourceRoot).Path
    $required = @(
        (Join-Path $SourceRoot 'analysis\REPORT.md'),
        (Join-Path $SourceRoot 'analysis\summary.json'),
        (Join-Path $SourceRoot 'execution_manifest.json'),
        (Join-Path $SourceRoot 'training\design.json'),
        (Join-Path $SourceRoot 'training\environment.json'),
        (Join-Path $SourceRoot 'training\GRID_COMPLETE.json'),
        (Join-Path $SourceRoot 'evaluation\design.json'),
        (Join-Path $SourceRoot 'evaluation\GRID_COMPLETE.json')
    )
    foreach ($path in $required) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Missing completed Stage-F artifact: $path"
        }
    }

    $files = @()
    $analysisRoot = Join-Path $SourceRoot 'analysis'
    $files += Get-ChildItem -LiteralPath $analysisRoot -File -Recurse | ForEach-Object {
        $relative = $_.FullName.Substring($analysisRoot.Length).TrimStart('\','/')
        [pscustomobject]@{
            Source = $_.FullName
            Destination = "$DestinationPrefix/" + ($relative -replace '\\','/')
        }
    }

    $files += @(
        [pscustomobject]@{ Source = Join-Path $SourceRoot 'execution_manifest.json'; Destination = "$DestinationPrefix/execution_manifest.json" },
        [pscustomobject]@{ Source = Join-Path $SourceRoot 'training\design.json'; Destination = "$DestinationPrefix/training_design.json" },
        [pscustomobject]@{ Source = Join-Path $SourceRoot 'training\environment.json'; Destination = "$DestinationPrefix/training_environment.json" },
        [pscustomobject]@{ Source = Join-Path $SourceRoot 'training\GRID_COMPLETE.json'; Destination = "$DestinationPrefix/training_grid_complete.json" },
        [pscustomobject]@{ Source = Join-Path $SourceRoot 'evaluation\design.json'; Destination = "$DestinationPrefix/evaluation_design.json" },
        [pscustomobject]@{ Source = Join-Path $SourceRoot 'evaluation\GRID_COMPLETE.json'; Destination = "$DestinationPrefix/evaluation_grid_complete.json" }
    )

    $files = $files | Sort-Object Destination -Unique
    Write-Host "Stage-F source root: $SourceRoot"
    Write-Host "Files to stage: $($files.Count)"
    Write-Host ''

    foreach ($file in $files) {
        $blob = (& git hash-object -w -- $file.Source).Trim()
        if ($LASTEXITCODE -ne 0 -or -not $blob) {
            throw "git hash-object failed for: $($file.Source)"
        }

        & git update-index --add --cacheinfo 100644 $blob $file.Destination
        if ($LASTEXITCODE -ne 0) {
            throw "git update-index failed for: $($file.Destination)"
        }

        & git update-index --skip-worktree -- $file.Destination
        if ($LASTEXITCODE -ne 0) {
            throw "Could not mark skip-worktree: $($file.Destination)"
        }

        Write-Host "STAGED $($file.Destination)"
    }

    Write-Host ''
    Write-Host 'Stage-F paper-facing results are staged directly in Git.'
    Write-Host 'Raw checkpoints/evaluator JSONs remain outside the repository.'
    Write-Host 'Review with: git diff --cached --stat'
    Write-Host 'Then commit and push normally.'
}
finally {
    Pop-Location
}
