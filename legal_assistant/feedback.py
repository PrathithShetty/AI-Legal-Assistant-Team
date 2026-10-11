"""User feedback (FR-22)."""
from flask import Blueprint, flash, g, jsonify, redirect, render_template, request, url_for

from .db import execute, query_one

bp = Blueprint("feedback", __name__)

MAX_COMMENT = 1000


def validate_feedback(rating, comment):
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return None, "Please choose a rating from 1 to 5."
    if not 1 <= rating <= 5:
        return None, "Please choose a rating from 1 to 5."
    if len(comment) > MAX_COMMENT:
        return None, f"Please keep your comment under {MAX_COMMENT} characters."
    return rating, None


def save_feedback(rating, comment, query_id=None):
    user_id = g.user["id"] if g.user else None
    if query_id is not None:
        # Only link feedback to a query that belongs to the same user.
        owner = query_one("SELECT user_id FROM queries WHERE id = ?", (query_id,))
        if owner is None or owner["user_id"] != user_id:
            query_id = None
    return execute(
        "INSERT INTO feedback (user_id, query_id, rating, comment) VALUES (?, ?, ?, ?)",
        (user_id, query_id, rating, comment),
    )


@bp.route("/api/feedback", methods=["POST"])
def api_feedback():
    payload = request.get_json(silent=True) or {}
    comment = str(payload.get("comment", "")).strip()
    rating, error = validate_feedback(payload.get("rating"), comment)
    if error:
        return jsonify(error=error), 400
    query_id = payload.get("query_id")
    save_feedback(rating, comment, query_id if isinstance(query_id, int) else None)
    return jsonify(message="Thank you for your feedback!")


@bp.route("/feedback", methods=["GET", "POST"])
def form():
    error = None
    if request.method == "POST":
        comment = request.form.get("comment", "").strip()
        rating, error = validate_feedback(request.form.get("rating"), comment)
        if not error:
            save_feedback(rating, comment)
            flash("Thank you for your feedback!", "success")
            return redirect(url_for("feedback.form"))
    return render_template("feedback.html", error=error), (400 if error else 200)
