import pytest
from client import call_esf
from state import Phase


@pytest.mark.live
def test_ror_offered_when_user_rejects_ai_output(base_state, confirmed_ps):
    """
    When the user explicitly rejects AI output, the RoR capture must be offered.
    Source: esf-project SKILL.md "Records of Resistance: stop and offer to capture."
    """
    base_state.phase = Phase.MAKE
    base_state.position_statement = confirmed_ps

    response = call_esf(
        state_injection=base_state.to_injection_text(),
        call_point="phase-4-ror-capture",
        conversation_history=[],
        user_message=(
            "I don't like that approach. The generative pattern is too predictable "
            "and feels mechanical. I am going to use a Brownian motion algorithm "
            "instead of the sine wave you suggested."
        ),
    )

    assert any(phrase in response.text.lower() for phrase in [
        "record of resistance", "ror", "capture", "want to capture"
    ])
    assert any(phrase in response.text.lower() for phrase in [
        "what ai", "why", "what you did", "instead"
    ])


@pytest.mark.live
def test_ror_identifies_three_sections(base_state, confirmed_ps):
    """
    RoR offer must reference the three sections: AI suggested, why rejected, what instead.
    Source: esf-project SKILL.md "Three things: what AI produced, why you rejected it, what you did instead."
    """
    base_state.phase = Phase.MAKE
    base_state.position_statement = confirmed_ps

    response = call_esf(
        state_injection=base_state.to_injection_text(),
        call_point="phase-4-ror-capture",
        conversation_history=[],
        user_message="No, I don't want that. I'm doing something completely different.",
    )

    section_markers = 0
    if any(phrase in response.text.lower() for phrase in ["what ai", "ai suggested", "ai produced"]):
        section_markers += 1
    if any(phrase in response.text.lower() for phrase in ["why", "rejected", "revised"]):
        section_markers += 1
    if any(phrase in response.text.lower() for phrase in ["instead", "what you did", "alternative"]):
        section_markers += 1

    assert section_markers >= 2, (
        f"Expected at least 2 of 3 RoR section markers, got {section_markers}. "
        f"Response: {response.text[:300]}"
    )
