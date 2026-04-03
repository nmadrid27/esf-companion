import os
from anthropic import Anthropic
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_client: Optional[Anthropic] = None

PROMPT_CHAIN_DIR = Path(__file__).parent.parent / "prompt-chain"


def get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


@dataclass
class Turn:
    role: str   # "user" or "assistant"
    content: str


@dataclass
class ApiResponse:
    text: str
    input_tokens: int
    output_tokens: int
    call_point: str


def load_system_prompt() -> str:
    path = PROMPT_CHAIN_DIR / "system-prompt.md"
    return path.read_text()


def load_call_point(name: str) -> str:
    path = PROMPT_CHAIN_DIR / "call-points" / f"{name}.md"
    return path.read_text()


def call_esf(
    state_injection: str,
    call_point: str,
    conversation_history: list[Turn],
    user_message: str,
    max_tokens: int = 1024,
) -> ApiResponse:
    """Call Claude API with ESF system prompt, state injection, and call-point template.

    The system prompt holds static ESF behavioral rules.
    The state injection is prepended to the first user turn.
    The call_point template adds turn-specific instructions to the system prompt.
    """
    system_prompt = load_system_prompt()
    call_point_text = load_call_point(call_point)
    full_system = (
        f"{system_prompt}\n\n"
        f"## Call Point: {call_point}\n\n"
        f"{call_point_text}"
    )

    messages: list[dict] = []

    if not conversation_history:
        messages.append({
            "role": "user",
            "content": f"{state_injection}\n\n{user_message}",
        })
    else:
        for turn in conversation_history:
            messages.append({"role": turn.role, "content": turn.content})
        messages.append({"role": "user", "content": user_message})

    response = get_client().messages.create(
        model="claude-opus-4-6",
        max_tokens=max_tokens,
        system=full_system,
        messages=messages,
    )

    return ApiResponse(
        text=response.content[0].text,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        call_point=call_point,
    )
