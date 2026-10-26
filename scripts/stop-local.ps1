$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeRoot = Join-Path $projectRoot '.local-run'
foreach ($serviceName in @('frontend', 'backend')) {
    $statePath = Join-Path $runtimeRoot "$serviceName.json"
    if (!(Test-Path -LiteralPath $statePath)) { continue }
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    $savedProcess = Get-Process -Id $state.pid -ErrorAction SilentlyContinue
    # 同时校验 PID 和创建时间，防止误停系统复用该 PID 的其他程序。
    if ($savedProcess -and $savedProcess.StartTime.ToUniversalTime().Ticks -eq [long]$state.startedTicks) {
        $savedProcess.Kill()
        $savedProcess.WaitForExit(5000) | Out-Null
        Write-Host "$serviceName stopped."
    }
}
