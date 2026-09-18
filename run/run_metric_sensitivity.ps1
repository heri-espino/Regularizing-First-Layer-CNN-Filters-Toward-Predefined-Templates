$script = Join-Path $PSScriptRoot '..\studies\cnn_metric_sensitivity\run_metric_sensitivity.ps1'
& $script @args
exit $LASTEXITCODE
