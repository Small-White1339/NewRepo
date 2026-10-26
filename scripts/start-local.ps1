$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $projectRoot 'backend'
$frontendRoot = Join-Path $projectRoot 'frontend'
$runtimeRoot = Join-Path $projectRoot '.local-run'
$backendPython = Join-Path $backendRoot '.venv/Scripts/python.exe'
$viteEntry = Join-Path $frontendRoot 'node_modules/vite/bin/vite.js'
if (!(Test-Path -LiteralPath $backendPython) -or !(Test-Path -LiteralPath $viteEntry)) {
    throw 'Dependencies are missing. Follow README.md to install backend and frontend dependencies first.'
}
$nodeCommand = (Get-Command node -ErrorAction Stop).Source
New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null

# 只创建缺失的本地配置，不覆盖已有 API Key。
$envPath = Join-Path $backendRoot '.env'
if (!(Test-Path -LiteralPath $envPath)) {
    $secretBytes = New-Object byte[] 48
    $randomSource = [Security.Cryptography.RandomNumberGenerator]::Create()
    $randomSource.GetBytes($secretBytes)
    $randomSource.Dispose()
    $newSecret = [Convert]::ToBase64String($secretBytes)
    $envContent = [IO.File]::ReadAllText((Join-Path $backendRoot '.env.example'))
    $envContent = $envContent -replace '(?m)^SECRET_KEY=.*$', "SECRET_KEY=$newSecret"
    [IO.File]::WriteAllText($envPath, $envContent, [Text.UTF8Encoding]::new($false))
}

function Test-OwnedProcess($State) {
    $savedProcess = Get-Process -Id $State.pid -ErrorAction SilentlyContinue
    return $null -ne $savedProcess -and $savedProcess.StartTime.ToUniversalTime().Ticks -eq [long]$State.startedTicks
}

function Start-LocalService($Name, $Executable, $Arguments, $Directory, $Port, $HealthUrl) {
    $statePath = Join-Path $runtimeRoot "$Name.json"
    $listening = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    if ($listening) {
        if (!(Test-Path -LiteralPath $statePath)) { throw "Port $Port is occupied by another program." }
        $previousState = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
        if (!(Test-OwnedProcess $previousState)) { throw "Port $Port is occupied by another program." }
        if ($listening.OwningProcess -notcontains [int]$previousState.pid) {
            # Windows 虚拟环境的 Python 启动器会创建实际监听端口的子进程。
            $listenerProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($listening[0].OwningProcess)"
            if ($listenerProcess.ParentProcessId -ne [int]$previousState.pid) {
                throw "Port $Port does not belong to the saved SmartHire process."
            }
        }
    } else {
        $launched = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $Directory `
            -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtimeRoot "$Name.out.log") `
            -RedirectStandardError (Join-Path $runtimeRoot "$Name.err.log")
        @{ pid = $launched.Id; startedTicks = $launched.StartTime.ToUniversalTime().Ticks } |
            ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
    }
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                $listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction Stop | Select-Object -First 1
                $readyProcess = Get-Process -Id $listener.OwningProcess -ErrorAction Stop
                @{ pid = $readyProcess.Id; startedTicks = $readyProcess.StartTime.ToUniversalTime().Ticks } |
                    ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
                return
            }
        } catch { }
        Start-Sleep -Milliseconds 500
    }
    throw "$Name did not become ready. Check logs in $runtimeRoot."
}

Push-Location $backendRoot
try {
    & $backendPython -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
} finally { Pop-Location }

Start-LocalService 'backend' $backendPython @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000') $backendRoot 8000 'http://127.0.0.1:8000/health'
Start-LocalService 'frontend' $nodeCommand @(('"' + $viteEntry + '"'), '--host', '127.0.0.1', '--port', '5180', '--strictPort') $frontendRoot 5180 'http://127.0.0.1:5180'
Write-Host 'SmartHire is running: http://127.0.0.1:5180'
Write-Host 'API documentation: http://127.0.0.1:8000/docs'
Write-Host 'Local demo account (SEED_ADMIN=true): admin / admin'
