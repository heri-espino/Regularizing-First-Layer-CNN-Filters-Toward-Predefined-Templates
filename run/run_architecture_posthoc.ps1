$script = Join-Path $PSScriptRoot '..\studies\cnn_architecture_posthoc\run_architecture_posthoc.ps1'
& $script @args
if ($null -ne $LASTEXITCODE) {
    exit $LASTEXITCODE
}
