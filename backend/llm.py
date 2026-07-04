"""Optional Claude layer.

If ANTHROPIC_API_KEY is set, Saathi uses Claude to re-voice the grounded reply
in the customer's language and register — warmer, simpler, vernacular. If no key
is present (or the SDK isn't installed), it silently falls back to the template
text, so the demo always runs.

Crucially, Claude is only allowed to rephrase. All numbers and product choices
come from the rules/journey layers and are passed in as fixed facts it must not
change. The model never becomes the source of a figure.
"""

from __future__ import annotations

import os

MODEL = "claude-haiku-4-5-20251001"  # fast + cheap for the conversational layer

_LANG_NAME = {"hi": "Hindi (written in Roman/Hinglish is fine)", "en": "English"}

_SYSTEM = (
    "You are Saathi, a friendly banking helper inside a mobile app. "
    "Re-voice the given message so it is warm, plain, and easy for someone with "
    "low financial literacy to understand. Keep it short (2-3 sentences). "
    "Do NOT add, remove or change any number, amount or product name. "
    "Do NOT give investment advice or make promises about returns. "
    "Reply ONLY in {lang}."
)


def rephrase(text: str, language: str) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return text
    try:
        import anthropic
    except ImportError:
        return text
    try:
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=_SYSTEM.format(lang=_LANG_NAME.get(language, "English")),
            messages=[{"role": "user", "content": text}],
        )
        out = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        return out.strip() or text
    except Exception:
        # Any API/network issue → fall back to the grounded template text.
        return text
