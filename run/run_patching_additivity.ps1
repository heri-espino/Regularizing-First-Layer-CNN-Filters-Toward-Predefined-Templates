$script = Join-Path $PSScriptRoot '..\studies\cnn_patching_additivity\run_patching_additivity.ps1'
& $script @args
if ($null -ne $LASTEXITCODE) {
    exit $LASTEXITCODE
}
