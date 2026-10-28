"""Generates the informational summary of a response (FR-07).

Sprint 1: the summary is built from the admin-approved knowledge base.
Sprint 2 adds an AI-written summary with this as the fallback.
"""


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
    """Return (summary_text, source)."""
    return knowledge_base_summary(category), "knowledge-base"
