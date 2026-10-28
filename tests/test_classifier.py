"""Member 2 - legal issue classification: FR-10."""
import json

import pytest

from legal_assistant.classifier import classify, score, tokenize
from legal_assistant.db import KNOWLEDGE_DIR

CATEGORIES = json.loads((KNOWLEDGE_DIR / "categories.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("question, expected", [
    ("I bought a mixer grinder and it stopped working, the shop refuses a replacement", "consumer"),
    ("My order from an e-commerce site was never delivered and there is no refund", "consumer"),
    ("My landlord is not returning my security deposit", "property"),
    ("The builder has delayed possession of my flat by two years", "property"),
    ("My husband and I want a divorce by mutual consent", "family"),
    ("My in-laws are harassing me for dowry", "family"),
    ("Someone stole my bike and the police are not registering an FIR", "criminal"),
    ("I was arrested and need bail", "criminal"),
    ("My company terminated me without notice and has not paid my salary", "employment"),
    ("How do I claim my PF and gratuity after resignation", "employment"),
    ("I lost money in a UPI fraud after sharing an OTP", "cyber"),
    ("Someone made a fake profile of me on Instagram", "cyber"),
    ("How do I file an RTI application to a government department", "rti"),
])
def test_classifies_common_questions(question, expected):
    category, _ = classify(question, CATEGORIES)
    assert category is not None and category["slug"] == expected


@pytest.mark.parametrize("question", [
    "What is a good recipe for pasta?",
    "Which football team will win the match tomorrow?",
])
def test_unrelated_questions_not_classified(question):
    category, s = classify(question, CATEGORIES)
    assert category is None and s == 0


def test_phrases_score_higher_than_words():
    assert score("security deposit", "security deposit") > score("deposit", "deposit")


def test_stemming_matches_plural_and_past_tense():
    words = tokenize("refunds evicted")
    assert "refund" in words and "evict" in words
