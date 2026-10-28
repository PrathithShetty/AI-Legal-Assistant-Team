"""Keyword-based legal issue classifier (FR-10).

Keywords come from the admin-managed categories table, so admins can improve classification without code changes.
Multi-word phrases score higher than single words because they are more specific.
"""
import re

PHRASE_WEIGHT = 2
WORD_WEIGHT = 1


def normalize(text):
    return re.sub(r"[^a-z0-9\s-]", " ", text.lower())


def tokenize(text):
    words = set()
    for token in normalize(text).split():
        words.add(token)
        # light stemming so "refunds", "evicted", "harassing" match "refund", "evict", "harass"
        for suffix in ("ing", "ed", "es", "s"):
            if token.endswith(suffix) and len(token) - len(suffix) >= 3:
                words.add(token[: -len(suffix)])
    return words


def split_keywords(keywords):
    return [k.strip().lower() for k in keywords.split(",") if k.strip()]


def score(text, keywords):
    padded = f" {' '.join(normalize(text).split())} "
    words = tokenize(text)
    total = 0
    for keyword in split_keywords(keywords):
        if " " in keyword or "-" in keyword:
            if f" {keyword} " in padded:
                total += PHRASE_WEIGHT
        elif keyword in words:
            total += WORD_WEIGHT
    return total


def classify(text, categories):
    """Return (category, score) for the best match, or (None, 0) if nothing matches.

    `categories` is a sequence of mappings with at least `slug` and `keywords`. Ties go to the earlier category.
    """
    best, best_score = None, 0
    for category in categories:
        s = score(text, category["keywords"])
        if s > best_score:
            best, best_score = category, s
    return best, best_score
