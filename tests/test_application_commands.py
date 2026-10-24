"""User-configured command templates match complete phrases in any language."""
import pytest
from jarvis.reply.application_commands import match_application_command

pytestmark=pytest.mark.unit

@pytest.mark.parametrize('text,templates,expected',[
    ('Jarvis, Telegramni och.', ['{application}ni och'],'telegram'),
    ('Telegram ilovasini och', ['{application}ni och','{application} ilovasini och'],'telegram'),
    ('Open Visual Studio Code', ['Open {application}'],'visual studio code'),
    ('Rechner öffnen', ['{application} öffnen'],'rechner'),
    ('Telegramni och degani nima?', ['{application}ni och'],None),
    ('Telegramni och', [],None),
    ('Telegramni och', ['(.*){application}ni och'],None),
])
def test_only_complete_configured_phrases_select_an_application(text,templates,expected):
    assert match_application_command(text,templates,['Jarvis']) == expected


@pytest.mark.parametrize('success,raw,key',[
    (True,'{"status":"launch_requested","application":"Actual App"}','launch_requested'),
    (False,'{"error":"not_installed"}','not_installed'),
    (False,'{"error":"ambiguous"}','ambiguous'),
    (True,'unstructured result','error'),
    (False,'{"error":[]}','error'),
])
def test_acknowledgements_depend_on_actual_structured_outcomes(success,raw,key):
    from jarvis.reply.application_commands import application_command_reply
    from jarvis.tools.types import ToolExecutionResult
    responses={name:name+' {application}' for name in ('launch_requested','not_installed','ambiguous','error')}
    reply=application_command_reply(ToolExecutionResult(success=success,reply_text=raw),'Requested',responses)
    assert reply.startswith(key+' ')
    assert ('Actual App' in reply) == (key=='launch_requested')
