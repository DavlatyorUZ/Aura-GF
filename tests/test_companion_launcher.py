"""Exercise the source launcher under Windows PowerShell without launching apps."""

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.skipif(os.name != 'nt', reason='Windows launcher')]


@pytest.mark.parametrize('environment', ['venv/Scripts', '.venv/Scripts', '.mamba_env'])
def test_launcher_resolves_its_folder_and_uses_windows_powershell_parameters(tmp_path, environment):
    root = tmp_path / 'Project with spaces'
    runtime = root / environment
    runtime.mkdir(parents=True)
    (runtime / 'pythonw.exe').touch()
    (runtime / 'python.exe').touch()
    shutil.copy(Path(__file__).parents[1] / 'Start_Jarvis.ps1', root)
    harness = root / 'harness.ps1'
    harness.write_text(r'''
$ErrorActionPreference = 'Stop'
$env:LOCALAPPDATA = $PSScriptRoot
function Get-CimInstance { return @() }
function Get-Process { return [pscustomobject]@{Id=42} }
function Start-Process {
    [CmdletBinding()]
    param($FilePath, $ArgumentList, $WorkingDirectory, $WindowStyle,
          [switch]$PassThru, $RedirectStandardOutput, $RedirectStandardError)
    @{exe=$FilePath; cwd=$WorkingDirectory; args=$ArgumentList;
      pythonpath=$env:PYTHONPATH; utf8=$env:PYTHONUTF8} |
        ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'launched.json')
    return [pscustomobject]@{Id=43; HasExited=$false}
}
& (Join-Path $PSScriptRoot 'Start_Jarvis.ps1')
''', encoding='utf-8-sig')
    completed = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                '-File', str(harness)], capture_output=True, text=True, timeout=20)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    launched = json.loads((root / 'launched.json').read_text(encoding='utf-8-sig'))
    assert Path(launched['exe']) == runtime / 'pythonw.exe'
    assert Path(launched['cwd']) == root
    assert Path(launched['pythonpath'].split(';')[0]) == root / 'src'
    assert launched['utf8'] == '1'
    assert launched['args'] == ['-m', 'desktop_app']
