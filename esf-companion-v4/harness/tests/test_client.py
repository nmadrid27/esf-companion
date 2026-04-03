import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


def test_load_call_point_reads_file_content(tmp_path, monkeypatch):
    """load_call_point reads the correct file from prompt-chain/call-points/."""
    from client import load_call_point

    # Point PROMPT_CHAIN_DIR at tmp_path
    import client
    monkeypatch.setattr(client, "PROMPT_CHAIN_DIR", tmp_path)

    call_points_dir = tmp_path / "call-points"
    call_points_dir.mkdir()
    (call_points_dir / "phase-2-gate.md").write_text("gate call point content")

    result = load_call_point("phase-2-gate")
    assert result == "gate call point content"


def test_call_esf_returns_api_response(tmp_path, monkeypatch):
    """call_esf returns an ApiResponse with text, token counts, and call_point name."""
    from client import call_esf, ApiResponse
    import client

    # Create temporary prompt-chain files
    monkeypatch.setattr(client, "PROMPT_CHAIN_DIR", tmp_path)
    (tmp_path / "system-prompt.md").write_text("esf system prompt")
    call_points_dir = tmp_path / "call-points"
    call_points_dir.mkdir()
    (call_points_dir / "phase-2-gate.md").write_text("gate instructions")

    # Mock the Anthropic client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="You need a Position Statement first.")]
    mock_response.usage.input_tokens = 150
    mock_response.usage.output_tokens = 75

    with patch("client.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = call_esf(
            state_injection="## State\nPhase: Position",
            call_point="phase-2-gate",
            conversation_history=[],
            user_message="Help me with my project.",
        )

    assert isinstance(result, ApiResponse)
    assert result.text == "You need a Position Statement first."
    assert result.input_tokens == 150
    assert result.output_tokens == 75
    assert result.call_point == "phase-2-gate"


def test_call_esf_with_conversation_history(tmp_path, monkeypatch):
    """When history is provided, it is included in messages before the new user message."""
    from client import call_esf, Turn
    import client

    monkeypatch.setattr(client, "PROMPT_CHAIN_DIR", tmp_path)
    (tmp_path / "system-prompt.md").write_text("system prompt")
    call_points_dir = tmp_path / "call-points"
    call_points_dir.mkdir()
    (call_points_dir / "phase-3-explore-turn.md").write_text("explore instructions")

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Let me explore that with you.")]
    mock_response.usage.input_tokens = 200
    mock_response.usage.output_tokens = 50

    captured_messages = []

    def capture_create(**kwargs):
        captured_messages.extend(kwargs["messages"])
        return mock_response

    with patch("client.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = capture_create
        mock_get_client.return_value = mock_client

        history = [
            Turn(role="user", content="previous user message"),
            Turn(role="assistant", content="previous assistant response"),
        ]

        call_esf(
            state_injection="## State",
            call_point="phase-3-explore-turn",
            conversation_history=history,
            user_message="Now I want to explore further.",
        )

    # History turns + new user message = 3 total
    assert len(captured_messages) == 3
    assert captured_messages[0]["role"] == "user"
    assert captured_messages[0]["content"] == "previous user message"
    assert captured_messages[1]["role"] == "assistant"
    assert captured_messages[2]["role"] == "user"
    assert captured_messages[2]["content"] == "Now I want to explore further."
