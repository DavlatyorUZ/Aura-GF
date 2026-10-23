param([switch]$DebugConsole)

$ErrorActionPreference = 'Stop'
$repoRoot = $PSScriptRoot
Set-Location -LiteralPath $repoRoot
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUNBUFFERED = '1'
$env:PYTHONPATH = Join-Path $repoRoot 'src'

try {
    $python = $null
    $interpreter = if ($DebugConsole) { 'python.exe' } else { 'pythonw.exe' }
    foreach ($folder in @('venv/Scripts', '.venv/Scripts', '.mamba_env')) {
        $candidate = Join-Path (Join-Path $repoRoot $folder) $interpreter
        if (Test-Path -LiteralPath $candidate) {
            $python = $candidate
            break
        }
    }
    if (-not $python) {
        throw 'Python environment not found. Install the source dependencies in venv, .venv or .mamba_env.'
    }

    $existing = Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe' OR Name = 'python.exe'" |
        Where-Object {
            $_.ExecutablePath -eq $python -and $_.CommandLine -match '\s-m\s+desktop_app(?:\s|$)'
        }
    if ($existing) {
        Write-Host 'ℹ️ Jarvis is already running. Use its tray icon or double-click the companion to open chat.'
        return
    }

    if (-not (Get-Process -Name 'ollama' -ErrorAction SilentlyContinue)) {
        $ollama = Join-Path $env:LOCALAPPDATA 'Programs/Ollama/ollama.exe'
        if (Test-Path -LiteralPath $ollama) {
            Write-Host '🦙 Starting local Ollama...'
            Start-Process -FilePath $ollama -ArgumentList 'serve' -WindowStyle Hidden
        }
    }

    if ($DebugConsole) {
        Write-Host '🚀 Starting Jarvis with diagnostic output...'
        & $python -m desktop_app
        exit $LASTEXITCODE
    }

    $logDir = Join-Path $env:LOCALAPPDATA 'Jarvis'
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    $stdout = Join-Path $logDir 'source-desktop.log'
    $stderr = Join-Path $logDir 'source-desktop-errors.log'
    $process = Start-Process -FilePath $python -ArgumentList '-m', 'desktop_app' `
        -WorkingDirectory $repoRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    Start-Sleep -Milliseconds 600
    if ($process.HasExited) {
        throw "Jarvis exited during startup. See $stderr"
    }
    Write-Host '🚀 Jarvis is starting. Double-click the companion to open chat.'
    Write-Host "  📄 Startup diagnostics: $stderr"
} catch {
    Write-Host "❌ $($_.Exception.Message)"
    exit 1
}
