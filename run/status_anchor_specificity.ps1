param(
    [string]$OutputRoot = $(if ($env:STAGE_G_ROOT) {
        $env:STAGE_G_ROOT
    } else {
        Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\anchor_specificity_cuda_001'
    })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Expected = 25600
$TrainingRoot = Join-Path $OutputRoot 'training'
$EvaluationRoot = Join-Path $OutputRoot 'evaluation'
$AnalysisRoot = Join-Path $OutputRoot 'analysis'

Write-Host 'Anchor-specificity run status'
Write-Host "Root: $OutputRoot"
Write-Host ''

if (-not (Test-Path -LiteralPath $OutputRoot)) {
    Write-Host 'Run root does not exist yet.'
    exit 0
}

function Count-Files([string]$Root, [string]$Filter) {
    if (-not (Test-Path -LiteralPath $Root)) { return 0 }
    return (Get-ChildItem -LiteralPath $Root -Filter $Filter -File -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
}

$TrainingComplete = Count-Files $TrainingRoot 'complete.json'
$Checkpoints = Count-Files $TrainingRoot 'epoch_0200.pt'
$Evaluations = if (Test-Path -LiteralPath (Join-Path $EvaluationRoot 'runs')) {
    (Get-ChildItem -LiteralPath (Join-Path $EvaluationRoot 'runs') -Filter 'epoch_*.json' -File -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
} else { 0 }

$TrainingMarker = Test-Path -LiteralPath (Join-Path $TrainingRoot 'GRID_COMPLETE.json')
$EvaluationMarker = Test-Path -LiteralPath (Join-Path $EvaluationRoot 'GRID_COMPLETE.json')
$AnalysisReport = Test-Path -LiteralPath (Join-Path $AnalysisRoot 'REPORT.md')

$TrainingPct = 100.0 * $TrainingComplete / $Expected
$EvaluationPct = 100.0 * $Evaluations / $Expected

Write-Host ("Training complete : {0,6} / {1} ({2:N2}%)" -f $TrainingComplete, $Expected, $TrainingPct)
Write-Host ("Final checkpoints  : {0,6} / {1}" -f $Checkpoints, $Expected)
Write-Host ("Evaluations saved  : {0,6} / {1} ({2:N2}%)" -f $Evaluations, $Expected, $EvaluationPct)
Write-Host ("Training GRID_COMPLETE   : {0}" -f $TrainingMarker)
Write-Host ("Evaluation GRID_COMPLETE : {0}" -f $EvaluationMarker)
Write-Host ("Frozen analysis REPORT   : {0}" -f $AnalysisReport)
Write-Host ''
Write-Host 'This helper reports completion counts only; it does not inspect scientific outcomes.'
