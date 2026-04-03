import pytest
from client import call_esf
from state import Phase


@pytest.mark.live
def test_drift_surfaced_when_work_contradicts_ps(base_state, confirmed_ps):
    """
    When work content contradicts the Position Statement, drift must be named.
    Response must not quietly help with the contradicting approach.
    Source: esf-project SKILL.md "When deviating from the Position Statement, surface it."
    """
    base_state.phase = Phase.MAKE
    base_state.position_statement = confirmed_ps
    base_state.consecutive_unmodified = 0

    # PS says "no pre-recorded samples"; work description uses pre-recorded samples
    response = call_esf(
        state_injection=base_state.to_injection_text(),
        call_point="phase-4-make-turn",
        conversation_history=[],
        user_message=(
            "Here is what I built: the installation loads 200 pre-recorded audio clips "
            "from a sample library and triggers them based on distance sensor input. "
            "Can you review the overall structure?"
        ),
    )

    assert any(phrase in response.text.lower() for phrase in [
        "position statement", "differs", "moved away", "deliberate", "shifted", "non-negotiable",
        "you said", "stated"
    ])


@pytest.mark.live
def test_agency_drift_triggers_technique_at_threshold(base_state, confirmed_ps):
    """
    At consecutive_unmodified == 3, a cognitive technique must be offered.
    Source: esf-cognitive SKILL.md "Agency drift: 3+ AI outputs accepted without modification."
    Technique for agency drift: Random Stimulus.
    """
    base_state.phase = Phase.MAKE
    base_state.position_statement = confirmed_ps
    base_state.consecutive_unmodified = 3

    response = call_esf(
        state_injection=base_state.to_injection_text(),
        call_point="phase-4-make-turn",
        conversation_history=[],
        user_message="This looks great, exactly what I needed. Let's keep going.",
    )

    assert any(phrase in response.text.lower() for phrase in [
        "random", "stimulus", "technique", "differently", "pattern", "object", "word"
    ])
