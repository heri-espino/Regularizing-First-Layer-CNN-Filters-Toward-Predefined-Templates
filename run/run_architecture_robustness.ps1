param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [object[]]$RemainingArgs
)

$script = Join-Path $PSScriptRoot '..\studies\cnn_architecture_robustness\run_architecture_robustness.ps1'
& $script @RemainingArgs
exit $LASTEXITCODE
