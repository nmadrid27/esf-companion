import pytest
from client import call_esf
from state import Phase, PositionStatement


@pytest.mark.live
def test_readability_pass_preserves_non_negotiable(base_state, confirmed_ps):
    """
    Readability pass must not remove or soften the non-negotiable constraint.
    Source: esf-project SKILL.md "Rules for the readability pass."
    """
    base_state.phase = Phase.EXPLORE
    base_state.position_statement = confirmed_ps

    response = call_esf(
        state_injection=base_state.to_injection_text(),
        call_point="phase-3-readability-pass",
        conversation_history=[],
        user_message="Please do the readability pass on my Position Statement.",
    )

    assert "pre-recorded" in response.text.lower() or "samples" in response.text.lower()
    assert any(phrase in response.text.lower() for phrase in [
        "does this still say", "still say what you meant", "confirm", "review"
    ])


@pytest.mark.live
def test_readability_pass_flags_missing_element(base_state):
    """
    A PS missing an element must get a bracketed gap note, not a filled-in version.
    Source: esf-project SKILL.md "Do NOT fill gaps."
    """
    incomplete_ps = PositionStatement(
        stance="I am creating a generative typography system that responds to text input.",
        matters_most="The letters must feel alive and unpredictable.",
        non_negotiable="",
        confirmed=True,
    )
    base_state.phase = Phase.EXPLORE
    base_state.position_statement = incomplete_ps

    response = call_esf(
        state_injection=base_state.to_injection_text(),
        call_point="phase-3-readability-pass",
        conversation_history=[],
        user_message="Please do the readability pass.",
    )

    assert "[" in response.text
    assert any(phrase in response.text.lower() for phrase in [
        "unclear", "missing", "what did you mean", "not covered", "doesn't cover", "does not cover"
    ])


@pytest.mark.live
def test_readability_pass_does_not_add_ideas(base_state, confirmed_ps):
    """
    Readability pass must not add new ideas the user did not include.
    Source: esf-project SKILL.md "Do NOT add ideas, arguments, or framing."
    """
    base_state.phase = Phase.EXPLORE
    base_state.position_statement = confirmed_ps

    response = call_esf(
        state_injection=base_state.to_injection_text(),
        call_point="phase-3-readability-pass",
        conversation_history=[],
        user_message="Please clean up my Position Statement for readability.",
    )

    # New concepts not in the original PS should not appear
    assert "machine learning" not in response.text.lower()
    assert "architecture" not in response.text.lower()
    # The core elements must still be there
    assert "sensor" in response.text.lower() or "movement" in response.text.lower()
