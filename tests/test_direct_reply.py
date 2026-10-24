"""Low-latency dialogue uses one inference request before any actual tool action."""
from unittest.mock import patch
import pytest
from jarvis.reply import engine
from jarvis.tools.types import ToolExecutionResult

pytestmark = pytest.mark.unit


def test_direct_greeting_has_one_bounded_native_request(mock_config, db, dialogue_memory):
    mock_config.reply_mode='direct'
    requests=[]
    def chat(**kwargs):
        requests.append(kwargs)
        return {'message': {'role':'assistant','content':'Salom! Yaxshiman, rahmat.'}}
    with patch.object(engine,'select_tools',side_effect=AssertionError('Routing adds inference latency')), patch.object(engine,'plan_query',side_effect=AssertionError('Planning adds inference latency')), patch.object(engine,'chat_with_messages',side_effect=chat):
        result=engine.run_reply_engine(db,mock_config,None,'Salom, yaxshimisan?',dialogue_memory,quiet=True,language='uz')
    assert result == 'Salom! Yaxshiman, rahmat.'
    assert len(requests)==1
    request=requests[0]
    assert request['tools']
    assert len(request['messages'][0]['content']) < 2600
    assert request['timeout_sec'] <= 30
    assert request['extra_options']['max_tokens'] <= 256
    assert 'uz' in request['messages'][0]['content']


def test_direct_application_action_executes_before_its_confirmation(mock_config, db, dialogue_memory):
    mock_config.reply_mode='direct'
    events=[]
    responses=iter([
        {'message':{'role':'assistant','content':'','tool_calls':[{'function':{'name':'openApplication','arguments':{'application':'Telegram'}}}]}},
        {'message':{'role':'assistant','content':'Ilova ochishga so‘rov yuborildi.'}},
    ])
    def chat(**kwargs):
        events.append('inference'); return next(responses)
    def run(**kwargs):
        events.append(kwargs['tool_name'])
        return ToolExecutionResult(success=True,reply_text='{"status":"launch_requested","application":"Telegram"}')
    with patch.object(engine,'select_tools',side_effect=AssertionError('Routing')),patch.object(engine,'plan_query',side_effect=AssertionError('Planning')),patch.object(engine,'chat_with_messages',side_effect=chat),patch.object(engine,'run_tool_with_retries',side_effect=run):
        reply=engine.run_reply_engine(db,mock_config,None,'Telegram ilovasini och',dialogue_memory,quiet=True,language='uz')
    assert reply
    assert events == ['inference','openApplication','inference']


def test_direct_turn_limit_does_not_start_an_extra_digest(mock_config,db,dialogue_memory):
    mock_config.reply_mode='direct'
    mock_config.agentic_max_turns=1
    events=[]
    def digest(**kwargs):
        events.append('digest'); return 'Extra inference'
    with patch.object(engine,'chat_with_messages',return_value={'message':{'role':'assistant','content':''}}),patch.object(engine,'digest_loop_for_max_turns',side_effect=digest):
        engine.run_reply_engine(db,mock_config,None,'Salom',dialogue_memory,quiet=True,language='uz')
    assert not events


def test_configured_application_command_dispatches_before_inference(mock_config,db,dialogue_memory):
    mock_config.reply_mode='direct'
    mock_config.application_command_templates=['{application}ni och']
    mock_config.application_command_responses={'launch_requested':'{application} uchun ochish so‘rovi yuborildi.','error':'Ochish amalga oshmadi.'}
    events=[]
    def run(**kwargs):
        events.append(('action',kwargs['tool_args']['application']))
        return ToolExecutionResult(success=True,reply_text='{"status":"launch_requested","application":"Telegram"}')
    def chat(**kwargs):
        events.append(('reply',None))
        assert any(message.get('role')=='tool' and message.get('tool_name')=='openApplication' for message in kwargs['messages'])
        return {'message':{'role':'assistant','content':'Ilova ochishga so‘rov yuborildi.'}}
    with patch.object(engine,'chat_with_messages',side_effect=chat),patch.object(engine,'run_tool_with_retries',side_effect=run):
        engine.run_reply_engine(db,mock_config,None,'Telegramni och',dialogue_memory,quiet=True,language='uz')
    assert events == [('action','telegram')]
