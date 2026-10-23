# Start Ollama server in background
$exe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
if (-not (Test-Path $exe)) {
    Write-Error "Ollama executable not found at $exe"
    exit 1
}

$running = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if ($running) {
    Write-Host "✅ Ollama is already running (PID: $($running.Id -join ', '))."
} else {
    Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine = "`"$exe`" serve"} | Out-Null
    Start-Sleep -Seconds 3
    Write-Host "🚀 Ollama server started successfully on http://127.0.0.1:11434"
}
