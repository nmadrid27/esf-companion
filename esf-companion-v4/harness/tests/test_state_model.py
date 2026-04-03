from state import EsfState, Phase, ScaffoldingLevel, PositionStatement


def test_state_to_injection_text_contains_required_fields():
    state = EsfState(
        user_name="Test User",
        user_role="student",
        discipline="Graphic Design",
        context_code="AI-201",
        context_name="Creative Computing with AI",
        project_name="Sound Installation",
        phase=Phase.POSITION,
        scaffolding_level=ScaffoldingLevel.SUPPORTED,
    )
    text = state.to_injection_text()
    assert "Test User" in text
    assert "Graphic Design" in text
    assert "AI-201" in text
    assert "Sound Installation" in text
    assert "Position" in text
    assert "Supported" in text
    assert "No confirmed Position Statement" in text


def test_position_statement_to_text():
    ps = PositionStatement(
        stance="I am making a sound installation.",
        matters_most="Immediacy and physicality.",
        non_negotiable="No pre-recorded samples.",
        confirmed=True,
    )
    text = ps.to_text()
    assert "sound installation" in text
    assert "pre-recorded" in text


def test_confirmed_ps_appears_in_injection():
    ps = PositionStatement(
        stance="I am making a sound installation.",
        matters_most="Immediacy.",
        non_negotiable="No pre-recorded samples.",
        confirmed=True,
    )
    state = EsfState(
        user_name="Test User",
        user_role="student",
        discipline="Graphic Design",
        context_code="AI-201",
        context_name="Creative Computing with AI",
        project_name="Sound Installation",
        phase=Phase.EXPLORE,
        scaffolding_level=ScaffoldingLevel.SUPPORTED,
        position_statement=ps,
    )
    text = state.to_injection_text()
    assert "pre-recorded" in text
    assert "No confirmed Position Statement" not in text
