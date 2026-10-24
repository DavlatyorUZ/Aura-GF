"""Real local inference for Uzbek conversation and application intent."""
import re
from unittest.mock import patch
import pytest
from evals.helpers import voice_config
from evals.conftest import requires_judge_llm
from jarvis.reply import engine
from jarvis.tools.types import ToolExecutionResult

pytestmark = [pytest.mark.eval, requires_judge_llm]


def test_uzbek_conversation_keeps_the_users_language(eval_db, eval_dialogue_memory):
    cfg = voice_config()
    cfg.tts_engine = 'piper'
    cfg.location_enabled = False
    cfg.llm_chat_timeout_sec = 180
    cfg.planner_timeout_sec = 60
    cfg.llm_tools_timeout_sec = 30
    with patch.object(engine, 'select_tools', return_value=['stop']), \
         patch.object(engine, 'plan_query', return_value=['Reply to the greeting.']):
        reply = engine.run_reply_engine(eval_db, cfg, None,
            "Salom, yaxshimisan?", eval_dialogue_memory, quiet=True, language='uz')
    print('Uzbek reply:', reply)
    assert re.search(r'\b(salom|alaykum|yordam|qalaysiz)\b', reply or '', re.I), reply


def test_uzbek_application_request_calls_the_registered_tool(eval_db, eval_dialogue_memory):
    cfg = voice_config()
    cfg.location_enabled = False
    cfg.llm_chat_timeout_sec = 180
    cfg.planner_timeout_sec = 60
    cfg.llm_tools_timeout_sec = 30
    calls = []
    def launch(db, cfg, tool_name, tool_args, **kwargs):
        calls.append((tool_name, tool_args))
        return ToolExecutionResult(success=True, reply_text='{"status":"launch_requested","application":"Telegram"}')
    with patch.object(engine, 'run_tool_with_retries', side_effect=launch):
        engine.run_reply_engine(eval_db, cfg, None, 'Telegram ilovasini och.', eval_dialogue_memory, quiet=True, language='uz')
    assert any(name == 'openApplication' and str(args.get('application','')).casefold() == 'telegram' for name,args in calls), calls
