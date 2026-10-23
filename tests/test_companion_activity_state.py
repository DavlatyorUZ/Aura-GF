"""Tests for companion animation state and emotion transitions during chat."""

from unittest.mock import Mock, patch
import pytest

from desktop_app.app import JarvisSystemTray
from desktop_app.face_widget import Expression
from jarvis.activity import JarvisState, get_jarvis_state
import jarvis.daemon as daemon

pytestmark = pytest.mark.unit


def test_detect_reply_expression_identifies_emotions():
    detect = JarvisSystemTray._detect_reply_expression
    # Positive / cheerful
    assert detect("Salom! Sizga qanday yordam bera olaman?") in (Expression.HAPPY, Expression.CURIOUS)
    assert detect("Ajoyib, hammasi tayyor!") == Expression.EXCITED
    assert detect("Rahmat, juda xursandman!") in (Expression.HAPPY, Expression.EXCITED)
    assert detect("Great job! That is wonderful!") == Expression.EXCITED

    # Inquisitive / curious
    assert detect("Bu haqda ko'proq ma'lumot bera olasizmi?") == Expression.CURIOUS
    assert detect("What would you like to know next?") == Expression.CURIOUS

    # Apologetic / concerned
    assert detect("Kechirasiz, bu faylni topa olmadim.") == Expression.CONCERNED
    assert detect("Sorry, I could not complete the operation.") == Expression.CONCERNED


def test_submit_text_query_updates_activity_states(monkeypatch):
    observed_states = []
    state_mgr = get_jarvis_state()
    original_acquire = state_mgr.acquire_state

    def tracking_acquire(state, **kwargs):
        observed_states.append(state)
        return original_acquire(state, **kwargs)

    monkeypatch.setattr(state_mgr, "acquire_state", tracking_acquire)
    monkeypatch.setattr(daemon, "_global_dialogue_memory", Mock())
    monkeypatch.setattr(daemon, "_global_cfg", Mock(llm_chat_model="test-model"))
    monkeypatch.setattr(daemon, "_global_db", Mock())

    with patch("jarvis.reply.engine.run_reply_engine", return_value="Salom! Hammasi zo'r!"):
        daemon.submit_text_query("Salom", use_ipc=False)
        import time
        time.sleep(0.3)

    assert JarvisState.THINKING in observed_states
    assert JarvisState.SPEAKING in observed_states
