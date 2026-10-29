"""Generates the informational summary of a response (FR-07).

The AI only writes the plain-language summary. Category, procedure steps and references always come from the
admin-approved knowledge base, so they cannot be invented. If the AI is disabled, unavailable or declines, a
summary is built from the knowledge base instead, so the app always answers (NFR-14).
"""
import logging

import anthropic
from flask import current_app

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the explanation writer for an educational legal-information website for people in India.
You explain Indian law in simple, plain English for people with no legal background.

Rules:
- Give general information only. Never present an outcome as guaranteed; use words such as "usually", "may" or "generally" where the law depends on facts.
- Base your answer on Indian law. Criminal law references must use the Bharatiya Nyaya Sanhita, 2023 and the Bharatiya Nagarik Suraksha Sanhita, 2023, which replaced the IPC and CrPC from 1 July 2024.
- Use the approved category, steps and references provided with the question as your main basis. Do not cite any case or section that is not in the approved references.
- Do not repeat the steps or the references as lists; they are shown separately below your text. Explain the person's situation and their main options.
- If the matter is serious or depends on detailed facts, say clearly that they should consult a qualified advocate.
- If the question is not about a legal issue, say briefly that this assistant only handles legal questions.
- Write 2 or 3 short paragraphs, under 200 words in total, as plain text without headings, bullet points or markdown.
- Do not add a disclaimer; the website adds one."""


class AIUnavailable(Exception):
    pass


def _client():
    return anthropic.Anthropic(
        timeout=current_app.config["AI_TIMEOUT_SECONDS"],
        max_retries=1,
    )


def build_prompt(question, category, steps, references):
    lines = [f"Question from the user:\n{question}", ""]
    if category:
        lines.append(f"Approved category: {category['name']} - {category['description']}")
    else:
        lines.append("Approved category: none matched (the question may be outside the supported areas).")
    if steps:
        lines.append("Approved general steps (shown separately):")
        lines += [f"{i}. {s}" for i, s in enumerate(steps, 1)]
    if references:
        lines.append("Approved references (shown separately):")
        lines += [f"- {r['title']}: {r['description']}" for r in references]
    return "\n".join(lines)


def ai_summary(question, category, steps, references):
    """Ask Claude for the summary. Raises AIUnavailable on any failure so the caller can fall back."""
    try:
        response = _client().beta.messages.create(
            model=current_app.config["AI_MODEL"],
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            thinking={"type": "adaptive"},
            output_config={"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content": build_prompt(question, category, steps, references)}],
        )
    except anthropic.AuthenticationError as exc:
        raise AIUnavailable("invalid API key") from exc
    except anthropic.RateLimitError as exc:
        raise AIUnavailable("rate limited") from exc
    except anthropic.APIStatusError as exc:
        raise AIUnavailable(f"API error {exc.status_code}") from exc
    except anthropic.APIConnectionError as exc:
        raise AIUnavailable("network error or timeout") from exc

    if response.stop_reason == "refusal":
        raise AIUnavailable("model declined the request")
    text = "\n".join(b.text for b in response.content if b.type == "text").strip()
    if not text:
        raise AIUnavailable("empty response")
    return text


def knowledge_base_summary(category):
    if category is None:
        return (
            "I could not match your question to one of the legal areas this assistant supports yet: "
            "consumer protection, property and tenancy, family and marriage, criminal and police matters, "
            "employment, cyber crime and online fraud, and right to information. "
            "Try describing your problem in more detail, for example what happened, who is involved and what you want."
        )
    description = category["description"]
    return (
        f"Your question appears to relate to {category['name']}. "
        f"This area covers {description[:1].lower()}{description[1:]} "
        "The general steps below show how such issues are usually handled in India. "
        "The right option for you depends on your exact facts and documents."
    )


def summarize(question, category, steps, references):
    """Return (summary_text, source) where source is 'ai' or 'knowledge-base'."""
    if current_app.config["AI_ENABLED"]:
        try:
            return ai_summary(question, category, steps, references), "ai"
        except AIUnavailable as exc:
            log.warning("AI summary unavailable (%s); using knowledge base.", exc)
    return knowledge_base_summary(category), "knowledge-base"
