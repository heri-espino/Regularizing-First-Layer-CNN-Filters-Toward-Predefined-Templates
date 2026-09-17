param([Parameter(ValueFromRemainingArguments=$true)][string[]]$RunArgs)
$RepoRoot = Split-Path -Parent $PSScriptRoot
& (Join-Path $RepoRoot 'studies\cnn_release_experiment\run.ps1') @RunArgs
exit $LASTEXITCODE
