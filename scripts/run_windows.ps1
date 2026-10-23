Param()

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host "[jarvis] $msg" }

# Repo root
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$REPO_ROOT = Resolve-Path (Join-Path $SCRIPT_DIR '..')
Set-Location $REPO_ROOT

# Helper to set env vars for the current process
$env:PYTHONPATH = Join-Path $REPO_ROOT 'src'
if (-not $env:JARVIS_VOICE_DEBUG) { $env:JARVIS_VOICE_DEBUG = '0' }

# Check for existing venv or .venv
$venvPath = Join-Path $REPO_ROOT 'venv'
if (-not (Test-Path $venvPath)) {
  $venvPath = Join-Path $REPO_ROOT '.venv'
}
$venvPython = Join-Path $venvPath 'Scripts/python.exe'

if (Test-Path $venvPython) {
  Write-Info "Using Python virtual environment at '$venvPath'"
  Write-Info 'Starting desktop app...'
  & $venvPython -m desktop_app
  exit $LASTEXITCODE
}

# Fallback: micromamba
$micromamba = Get-Command micromamba -ErrorAction SilentlyContinue
if ($micromamba) {
  $envPrefix = Join-Path $REPO_ROOT '.mamba_env'
  $envPython = Join-Path $envPrefix 'python.exe'
  if (Test-Path $envPython) {
    Write-Info "Starting desktop app via Micromamba at '$envPrefix'..."
    & $envPython -m desktop_app
    exit $LASTEXITCODE
  }
}

Write-Error "No working Python virtual environment found. Please set up venv in $REPO_ROOT\venv"
