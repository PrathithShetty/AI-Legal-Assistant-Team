"""Legal query submission and structured responses (FR-05 to FR-09, FR-11, FR-20)."""
import json
import re
import time

from flask import Blueprint, current_app, g, jsonify, render_template, request

from . import ai, guidance
from .classifier import classify
from .db import execute, query_all
from .disclaimer import DISCLAIMER
from .references import NO_REFERENCE_MESSAGE, find_references

bp = Blueprint("query", __name__)

MIN_QUERY_LENGTH = 10

EXAMPLE_QUESTIONS = [
    "My landlord is not returning my security deposit after I vacated the flat.",
    "I ordered a phone online and received a damaged product. The seller refuses a refund.",
    "Someone took Rs. 20,000 from my account through a UPI fraud call.",
    "My employer has not paid my salary for two months.",
    "How do I file an RTI to know the status of my pension application?",
    "The police are refusing to register my complaint about a theft.",
]


def validate_query(text, max_length):
    """Return an error message, or None if the query is usable (FR-06)."""
    text = (text or "").strip()
    if not text:
        return "Please type your legal question."
    if len(text) > max_length:
        return f"Your question is too long. Please keep it under {max_length} characters."
    if len(text) < MIN_QUERY_LENGTH or len(re.findall(r"[A-Za-z]", text)) < 5:
        return "Please describe your problem in a few words, for example what happened and what you want."
    return None


def build_response(question):
    """Classify the question and assemble the structured response (FR-08)."""
    categories = query_all("SELECT * FROM categories ORDER BY id")
    category, _ = classify(question, categories)
    steps = guidance.procedure_steps(category)
    references = find_references(category["slug"] if category else None, question)
    needs_help, reasons = guidance.professional_help(question, category)
    summary, source = ai.summarize(question, category, steps, references)
    return {
        "question": question,
        "summary": summary,
        "source": source,
        "category": {"slug": category["slug"], "name": category["name"]} if category else None,
        "steps": steps,
        "references": references,
        "no_reference_message": None if references else NO_REFERENCE_MESSAGE,
        "professional_help": guidance.lawyer_message(reasons) if needs_help else None,
        "emergency": guidance.emergency_notices(question),
        "disclaimer": DISCLAIMER,
    }


@bp.route("/")
def home():
    return render_template("home.html", examples=EXAMPLE_QUESTIONS)


@bp.route("/api/query", methods=["POST"])
def api_query():
    started = time.perf_counter()
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    error = validate_query(question, current_app.config["MAX_QUERY_LENGTH"])
    if error:
        return jsonify(error=error), 400

    response = build_response(question)
    if g.user:  # FR-20: history is stored only for registered users
        response["query_id"] = execute(
            "INSERT INTO queries (user_id, query_text, category, response) VALUES (?, ?, ?, ?)",
            (g.user["id"], question, response["category"]["slug"] if response["category"] else None,
             json.dumps(response)),
        )
    else:
        response["query_id"] = None
    response["elapsed_ms"] = round((time.perf_counter() - started) * 1000)
    return jsonify(response)
