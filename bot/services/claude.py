import json
import anthropic
from bot.config import ANTHROPIC_API_KEY
from bot.prompts.system import get_system_prompt

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def classify_message(text: str) -> dict:
    """Send user message to Claude, get structured intent back."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=get_system_prompt(),
        messages=[{"role": "user", "content": text}],
    )
    raw = response.content[0].text.strip()
    # Strip markdown code blocks if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)
