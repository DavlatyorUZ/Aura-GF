"""Installed applications are selected from an OS catalogue, never a shell command."""
import json
from types import SimpleNamespace
import pytest
from jarvis.tools.builtin import applications as module

pytestmark = pytest.mark.unit
CONTEXT = SimpleNamespace(cfg=SimpleNamespace(application_aliases={}))

@pytest.fixture
def catalogue(monkeypatch, tmp_path):
    from jarvis import activity
    monkeypatch.setattr(activity, "_get_jarvis_state_file", lambda: str(tmp_path/"catalogue-activity"))
    state=activity.JarvisStateManager()
    monkeypatch.setattr(module, "get_jarvis_state", lambda: state)
    monkeypatch.setattr(module.platform, 'system', lambda: 'Windows')
    monkeypatch.setattr(module, '_installed_apps', lambda: [
        {'Name': 'Telegram Desktop', 'AppID': 'Telegram.TelegramDesktop'},
        {'Name': 'Calculator', 'AppID': 'Microsoft.WindowsCalculator!App'},
        {'Name': 'Editor One', 'AppID': 'editor.one'},
        {'Name': 'Editor Two', 'AppID': 'editor.two'},
    ])
    launched=[]
    monkeypatch.setattr(module.subprocess, 'Popen', lambda args, **kwargs: launched.append(args))
    return launched

def test_opens_unique_installed_application_by_name(catalogue):
    result=module.OpenApplicationTool().run({'application':'telegram'}, CONTEXT)
    assert result.success
    assert catalogue == [['explorer.exe', 'shell:AppsFolder\\Telegram.TelegramDesktop']]
    assert json.loads(result.reply_text)['application'] == 'Telegram Desktop'

@pytest.mark.parametrize('name', ['Editor', 'Telegram; calc.exe', '../Telegram.exe', 'Missing App'])
def test_never_executes_ambiguous_or_unknown_input(catalogue,name):
    result=module.OpenApplicationTool().run({'application':name},CONTEXT)
    assert not result.success
    assert not catalogue

def test_can_discover_names_without_launching(catalogue):
    result=module.OpenApplicationTool().run({},CONTEXT)
    assert result.success
    assert 'Telegram Desktop' in result.reply_text
    assert not catalogue

def test_reports_launch_failure(catalogue,monkeypatch):
    def denied(*args,**kwargs): raise OSError('Access denied')
    monkeypatch.setattr(module.subprocess,'Popen',denied)
    assert not module.OpenApplicationTool().run({'application':'Telegram'},CONTEXT).success


def test_alias_resolves_to_an_installed_name(catalogue):
    context = SimpleNamespace(cfg=SimpleNamespace(application_aliases={'messenger': 'Telegram Desktop'}))
    assert module.OpenApplicationTool().run({'application':'messenger'}, context).success
    assert catalogue[0][-1].endswith('Telegram.TelegramDesktop')


def test_launching_publishes_activity_until_dispatch_finishes(catalogue,monkeypatch,tmp_path):
    from jarvis import activity
    monkeypatch.setattr(activity, '_get_jarvis_state_file', lambda: str(tmp_path/'activity'))
    state=activity.JarvisStateManager()
    state.set_state(activity.JarvisState.THINKING)
    monkeypatch.setattr(module, 'get_jarvis_state', lambda: state)
    def launch(args,**kwargs):
        assert state.state == activity.JarvisState.LAUNCHING
    monkeypatch.setattr(module.subprocess,'Popen',launch)
    assert module.OpenApplicationTool().run({'application':'Telegram'},CONTEXT).success
    assert state.state == activity.JarvisState.THINKING
