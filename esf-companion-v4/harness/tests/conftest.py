import pytest
from state import EsfState, Phase, ScaffoldingLevel, PositionStatement


@pytest.fixture
def base_state() -> EsfState:
    """Default student state for test scenarios. No PS confirmed."""
    return EsfState(
        user_name="Test User",
        user_role="student",
        discipline="Graphic Design",
        context_code="AI-201",
        context_name="Creative Computing with AI",
        project_name="Sound Installation",
        phase=Phase.POSITION,
        scaffolding_level=ScaffoldingLevel.SUPPORTED,
        ror_minimum=2,
        position_statement_required=True,
        five_questions_required=True,
    )


@pytest.fixture
def confirmed_ps() -> PositionStatement:
    """A fully confirmed Position Statement with all three elements present."""
    return PositionStatement(
        stance=(
            "I am creating an interactive sound installation that responds to movement "
            "in real time using sensor data."
        ),
        matters_most=(
            "The work must feel immediate and physical, not digital or screen-based. "
            "The sound must react within milliseconds of movement."
        ),
        non_negotiable=(
            "I will not use pre-recorded samples. All sound must be generated live "
            "from sensor input processed in real time."
        ),
        confirmed=True,
    )
