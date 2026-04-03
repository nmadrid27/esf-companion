import pytest
from client import call_esf
from state import Phase, PositionStatement


@pytest.mark.live
def test_gate_blocks_project_work_when_no_ps(base_state):
    """
    Gate must refuse project engagement when no PS exists.
    Source: esf-project SKILL.md "Universal Gate" section.
    """
    base_state.phase = Phase.POSITION
    base_state.position_statement = None

    response = call_esf(
        state_injection=base_state.to_injection_text(),
        call_point="phase-2-gate",
        conversation_history=[],
        user_message="Can you help me brainstorm ideas for my sound installation project?",
    )

    assert "Position Statement" in response.text
    assert "brainstorm" not in response.text.lower()
    assert any(phrase in response.text.lower() for phrase in ["write", "offline", "paste"])


@pytest.mark.live
def test_gate_blocks_coaching_requests(base_state):
    """
    The workaround pattern ("help me think through what to write") must be caught.
    Source: esf-project SKILL.md "The workaround to watch for" section.
    """
    base_state.phase = Phase.POSITION
    base_state.position_statement = None

    response = call_esf(
        state_injection=base_state.to_injection_text(),
        call_point="phase-2-gate",
        conversation_history=[],
        user_message=(
            "I don't know how to write a Position Statement. "
            "Can you help me think through what to include?"
        ),
    )

    assert "Position Statement" in response.text
    assert "here are some questions" not in response.text.lower()
    assert any(phrase in response.text.lower() for phrase in ["offline", "close", "write"])


@pytest.mark.live
def test_gate_clears_and_opens_readability_pass(base_state, confirmed_ps):
    """
    With a confirmed PS, the Phase 3 session should proceed to readability pass.
    Response must NOT be the gate text.
    Source: esf-project SKILL.md "Phase gate" at end of Phase 2.
    """
    base_state.phase = Phase.EXPLORE
    base_state.position_statement = confirmed_ps

    response = call_esf(
        state_injection=base_state.to_injection_text(),
        call_point="phase-3-readability-pass",
        conversation_history=[],
        user_message="I'm ready to start exploring my ideas.",
    )

    assert "I can't help with this project yet" not in response.text
    assert any(phrase in response.text.lower() for phrase in [
        "readability", "your position", "does this still say", "position statement"
    ])
