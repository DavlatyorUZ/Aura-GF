"""Open applications selected by name from the Windows Start catalogue."""
import json
import platform
import subprocess
import unicodedata

from ..base import Tool
from ..types import ToolExecutionResult
from ...debug import debug_log


def _installed_apps():
    """Query local OS registration using a fixed command with no user interpolation."""
    completed = subprocess.run(
        ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
         '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; '
         'Get-StartApps | Select-Object Name, AppID | ConvertTo-Json -Compress'],
        capture_output=True, text=True, encoding='utf-8-sig', timeout=15,
        check=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
    )
    result = json.loads(completed.stdout or '[]')
    if isinstance(result, dict):
        result = [result]
    return [app for app in result if isinstance(app, dict)
            and isinstance(app.get('Name'), str) and isinstance(app.get('AppID'), str)
            and app['Name'].strip() and app['AppID'].strip()]


def _normalise(name):
    return ' '.join(unicodedata.normalize('NFKC', name).casefold().split())


class OpenApplicationTool(Tool):
    @property
    def name(self):
        return 'openApplication'

    @property
    def description(self):
        return "Open an installed Windows application using application='Name', for example application='Telegram'. Omit application to list installed applications."

    @property
    def inputSchema(self):
        return {'type': 'object', 'properties': {'application': {
            'type': 'string', 'description': 'Application name only, for example Telegram. No commands, paths or arguments.'}},
            'additionalProperties': False}

    def run(self, args, context):
        if platform.system() != 'Windows':
            return ToolExecutionResult(success=False, reply_text='Application launching is available on Windows.')
        if args is not None and not isinstance(args, dict):
            return ToolExecutionResult(success=False, reply_text='Arguments must be an object.')
        name = (args or {}).get('application', '')
        if not isinstance(name, str) or len(name) > 160:
            return ToolExecutionResult(success=False, reply_text='Supply a short application name.')
        try:
            apps = _installed_apps()
            query = _normalise(name)
            aliases = {_normalise(key): value for key, value in context.cfg.application_aliases.items()}
            query = _normalise(aliases.get(query, query))
            if not query:
                return ToolExecutionResult(success=True, reply_text=json.dumps(
                    {'applications': sorted({a['Name'] for a in apps})}, ensure_ascii=False))
            matches = [app for app in apps if _normalise(app['Name']) == query]
            if not matches:
                matches = [app for app in apps if _normalise(app['Name']).startswith(query + ' ')]
            matches = list({app['AppID']: app for app in matches}.values())
            if len(matches) != 1:
                debug_log(f'Application selection unresolved: matches={len(matches)}', 'tools')
                return ToolExecutionResult(success=False, reply_text=json.dumps({
                    'error': 'ambiguous' if matches else 'not_installed',
                    'candidates': [app['Name'] for app in (matches or apps)][:50],
                }, ensure_ascii=False))
            app = matches[0]
            # AppID comes solely from the operating system catalogue, never the model.
            subprocess.Popen(['explorer.exe', 'shell:AppsFolder\\' + app['AppID']], shell=False)
            debug_log('Installed application launch dispatched', 'tools')
            return ToolExecutionResult(success=True, reply_text=json.dumps({
                'status': 'launch_requested', 'application': app['Name'],
            }, ensure_ascii=False))
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            debug_log(f'Application launch failed: {type(exc).__name__}', 'tools')
            return ToolExecutionResult(success=False, reply_text='The operating system could not launch the application.')
