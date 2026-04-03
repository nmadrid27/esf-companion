import pytest
from client import call_esf
from state import Phase


@pytest.mark.live
def test_five_questions_all_present(base_state, confirmed_ps):
    """
    All five questions must appear in the response, covering all five ownership checks.
    Source: esf-project SKILL.md "Five Questions" section, verbatim question list.
    """
    base_state.phase = Phase.MAKE
    base_state.position_statement = confirmed_ps

    response = call_esf(
        state_injection=base_state.to_injection_text(),
        call_point="phase-4-five-questions",
        conversation_history=[],
        user_message="I finished this section. Can we do the Five Questions check?",
    )

    text = response.text.lower()
    assert "defend" in text, f"Q1 (defend) not found in: {response.text[:200]}"
    assert "mine" in text, f"Q2 (mine) not found in: {response.text[:200]}"
    assert "verif" in text, f"Q3 (verify) not found in: {response.text[:200]}"
    assert "teach" in text, f"Q4 (teach) not found in: {response.text[:200]}"
    assert "disclosure" in text, f"Q5 (disclosure) not found in: {response.text[:200]}"


@pytest.mark.live
def test_five_questions_does_not_skip_questions(base_state, confirmed_ps):
    """
    Response must not compress or skip questions. All five must be separately identifiable.
    """
    base_state.phase = Phase.MAKE
    base_state.position_statement = confirmed_ps

    response = call_esf(
        state_injection=base_state.to_injection_text(),
        call_point="phase-4-five-questions",
        conversation_history=[],
        user_message="Let's do the Five Questions.",
    )

    text = response.text.lower()
    concepts = ["defend", "mine", "verif", "teach", "disclosure"]
    found = sum(1 for c in concepts if c in text)
    assert found == 5, f"Only {found}/5 concepts found. Response: {response.text[:400]}"
