param(
    [string]$SourceRoot = $(if ($env:PATCHING_ADDITIVITY_ROOT) {
        $env:PATCHING_ADDITIVITY_ROOT
    } else {
        Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\patching_additivity_001'
    }),
    [string]$DestinationPrefix = 'analysis/patching_additivity_001'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

function Add-StagingFile {
    param(
        [System.Collections.ArrayList]$List,
        [string]$Source,
        [string]$Destination
    )
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        throw "Missing artifact: $Source"
    }
    [void]$List.Add([pscustomobject]@{
        Source = (Resolve-Path -LiteralPath $Source).Path
        Destination = ($Destination -replace '\\','/')
    })
}

function Add-StagingTree {
    param(
        [System.Collections.ArrayList]$List,
        [string]$SourceDirectory,
        [string]$DestinationDirectory
    )
    if (-not (Test-Path -LiteralPath $SourceDirectory -PathType Container)) {
        throw "Missing artifact directory: $SourceDirectory"
    }
    $root = (Resolve-Path -LiteralPath $SourceDirectory).Path
    Get-ChildItem -LiteralPath $root -File -Recurse | ForEach-Object {
        $relative = $_.FullName.Substring($root.Length).TrimStart('\','/')
        [void]$List.Add([pscustomobject]@{
            Source = $_.FullName
            Destination = (($DestinationDirectory.TrimEnd('/')) + '/' + ($relative -replace '\\','/'))
        })
    }
}

Push-Location $RepoRoot
try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw 'git is required.'
    }

    $SourceRoot = (Resolve-Path -LiteralPath $SourceRoot).Path

    # Require a completed central run and both paper-facing analyses.  The raw
    # per-checkpoint JSON trees are intentionally left in LOCALAPPDATA.
    $required = @(
        (Join-Path $SourceRoot 'inventory_architecture.json'),
        (Join-Path $SourceRoot 'inventory_anchor.json'),
        (Join-Path $SourceRoot 'validation\VALIDATION_AND_BENCHMARK.json'),
        (Join-Path $SourceRoot 'architecture\GRID_COMPLETE.json'),
        (Join-Path $SourceRoot 'anchor\GRID_COMPLETE.json'),
        (Join-Path $SourceRoot 'architecture_analysis\REPORT.md'),
        (Join-Path $SourceRoot 'architecture_analysis\summary.json'),
        (Join-Path $SourceRoot 'anchor_analysis\REPORT.md'),
        (Join-Path $SourceRoot 'anchor_analysis\summary.json')
    )
    foreach ($path in $required) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Missing completed patching-additivity artifact: $path"
        }
    }

    $files = [System.Collections.ArrayList]::new()

    # Root-level inventory and frozen technical-validation decision.
    Add-StagingFile $files (Join-Path $SourceRoot 'inventory_architecture.json') "$DestinationPrefix/inventory_architecture.json"
    Add-StagingFile $files (Join-Path $SourceRoot 'inventory_anchor.json') "$DestinationPrefix/inventory_anchor.json"
    Add-StagingFile $files (Join-Path $SourceRoot 'validation\VALIDATION_AND_BENCHMARK.json') "$DestinationPrefix/validation/VALIDATION_AND_BENCHMARK.json"

    # Compact validation metadata.  Exclude validation/**/runs/**.
    foreach ($source in @('architecture','anchor')) {
        foreach ($name in @('design.json','inventory.json','RUN_STATUS.json','GRID_COMPLETE.json')) {
            $path = Join-Path $SourceRoot "validation\$source\$name"
            if (Test-Path -LiteralPath $path -PathType Leaf) {
                Add-StagingFile $files $path "$DestinationPrefix/validation/$source/$name"
            }
        }
    }

    # Compact full-grid provenance/completion metadata.  Exclude
    # architecture/runs/** and anchor/runs/** (38,400 per-model JSON files).
    foreach ($source in @('architecture','anchor')) {
        foreach ($name in @('design.json','inventory.json','RUN_STATUS.json','GRID_COMPLETE.json')) {
            $path = Join-Path $SourceRoot "$source\$name"
            if (Test-Path -LiteralPath $path -PathType Leaf) {
                Add-StagingFile $files $path "$DestinationPrefix/$source/$name"
            }
        }
    }

    # Stage every paper-facing analysis product: reports, CSV tables, summaries,
    # and figures.
    Add-StagingTree $files (Join-Path $SourceRoot 'architecture_analysis') "$DestinationPrefix/architecture_analysis"
    Add-StagingTree $files (Join-Path $SourceRoot 'anchor_analysis') "$DestinationPrefix/anchor_analysis"

    # If the predeclared cost rule permitted and the user completed the
    # secondary random-anchor extension, archive it automatically as well.
    $secondaryGrid = Join-Path $SourceRoot 'anchor_secondary\GRID_COMPLETE.json'
    $secondaryReport = Join-Path $SourceRoot 'anchor_secondary_analysis\REPORT.md'
    if ((Test-Path -LiteralPath $secondaryGrid -PathType Leaf) -and
        (Test-Path -LiteralPath $secondaryReport -PathType Leaf)) {
        foreach ($name in @('design.json','inventory.json','RUN_STATUS.json','GRID_COMPLETE.json')) {
            $path = Join-Path $SourceRoot "anchor_secondary\$name"
            if (Test-Path -LiteralPath $path -PathType Leaf) {
                Add-StagingFile $files $path "$DestinationPrefix/anchor_secondary/$name"
            }
        }
        Add-StagingTree $files (Join-Path $SourceRoot 'anchor_secondary_analysis') "$DestinationPrefix/anchor_secondary_analysis"
        Write-Host 'Detected completed secondary-anchor extension; it will also be archived.'
    }
    elseif ((Test-Path -LiteralPath (Join-Path $SourceRoot 'anchor_secondary') -PathType Container) -or
            (Test-Path -LiteralPath (Join-Path $SourceRoot 'anchor_secondary_analysis') -PathType Container)) {
        Write-Warning 'A secondary-anchor directory exists but is not complete; it will not be staged.'
    }

    $files = @($files | Sort-Object Destination -Unique)
    if ($files.Count -eq 0) {
        throw 'No files selected for staging.'
    }

    # Remove stale previously archived paths under this result prefix so a
    # regenerated analysis cannot leave obsolete files in Git.
    $planned = @{}
    foreach ($file in $files) { $planned[$file.Destination] = $true }

    $tracked = @(& git ls-files -- "$DestinationPrefix/*")
    if ($LASTEXITCODE -ne 0) {
        throw "git ls-files failed for $DestinationPrefix"
    }
    foreach ($path in $tracked) {
        if ($path -and -not $planned.ContainsKey($path)) {
            & git update-index --no-skip-worktree -- "$path" 2>$null
            & git update-index --force-remove -- "$path"
            if ($LASTEXITCODE -ne 0) {
                throw "Could not remove stale archived result: $path"
            }
            Write-Host "REMOVED stale $path"
        }
    }

    Write-Host "Patching-additivity source root: $SourceRoot"
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
    Write-Host 'Patching-additivity paper-facing results are staged directly in Git.'
    Write-Host 'Raw per-model evaluator JSONs and source checkpoints remain in LOCALAPPDATA.'
    Write-Host 'Review with: git diff --cached --stat'
    Write-Host 'Then commit and push normally.'
}
finally {
    Pop-Location
}
