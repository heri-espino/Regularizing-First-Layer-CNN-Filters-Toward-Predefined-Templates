param(
    [string]$SourceRoot = $(if ($env:METRIC_SENSITIVITY_ROOT) {
        $env:METRIC_SENSITIVITY_ROOT
    } else {
        Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\metric_sensitivity_001'
    }),
    [string]$DestinationPrefix = 'analysis/metric_sensitivity_001'
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
        (Join-Path $SourceRoot 'stage_d\design.json'),
        (Join-Path $SourceRoot 'stage_d\EVAL_COMPLETE.json'),
        (Join-Path $SourceRoot 'stage_e\design.json'),
        (Join-Path $SourceRoot 'stage_e\EVAL_COMPLETE.json')
    )
    foreach ($path in $required) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Missing completed metric-sensitivity artifact: $path"
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
        [pscustomobject]@{
            Source = Join-Path $SourceRoot 'execution_manifest.json'
            Destination = "$DestinationPrefix/execution_manifest.json"
        },
        [pscustomobject]@{
            Source = Join-Path $SourceRoot 'stage_d\design.json'
            Destination = "$DestinationPrefix/stage_d_design.json"
        },
        [pscustomobject]@{
            Source = Join-Path $SourceRoot 'stage_d\EVAL_COMPLETE.json'
            Destination = "$DestinationPrefix/stage_d_eval_complete.json"
        },
        [pscustomobject]@{
            Source = Join-Path $SourceRoot 'stage_e\design.json'
            Destination = "$DestinationPrefix/stage_e_design.json"
        },
        [pscustomobject]@{
            Source = Join-Path $SourceRoot 'stage_e\EVAL_COMPLETE.json'
            Destination = "$DestinationPrefix/stage_e_eval_complete.json"
        }
    )

    $files = $files | Sort-Object Destination -Unique

    Write-Host "Source root: $SourceRoot"
    Write-Host "Repository:  $RepoRoot"
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

        # The university worktree may not allow the corresponding directory to
        # exist. Hide that local absence while keeping the blob staged.
        & git update-index --skip-worktree -- $file.Destination
        if ($LASTEXITCODE -ne 0) {
            throw "Could not mark skip-worktree: $($file.Destination)"
        }

        Write-Host "STAGED $($file.Destination)"
    }

    Write-Host ''
    Write-Host 'External metric-sensitivity results are staged in the Git index.'
    Write-Host 'No files were copied into the restricted worktree.'
    Write-Host ''
    Write-Host 'Review with:'
    Write-Host '  git diff --cached --stat'
    Write-Host '  git status'
    Write-Host ''
    Write-Host 'Then commit and push normally.'
}
finally {
    Pop-Location
}
