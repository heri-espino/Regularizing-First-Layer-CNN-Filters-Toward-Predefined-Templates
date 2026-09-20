$script = Join-Path $PSScriptRoot '..\studies\cnn_anchor_specificity\run_anchor_specificity.ps1'
& $script @args
if ($null -ne $LASTEXITCODE) {
    exit $LASTEXITCODE
}
