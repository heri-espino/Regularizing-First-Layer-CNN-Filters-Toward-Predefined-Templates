$script = Join-Path $PSScriptRoot '..\studies\cnn_architecture_robustness\run_architecture_robustness.ps1'
& $script @args
if ($null -ne $LASTEXITCODE) {
    exit $LASTEXITCODE
}
