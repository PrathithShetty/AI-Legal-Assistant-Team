"""My cases: saved questions of registered users with case status (FR-20, FR-21, NFR-07, NFR-09).

Every question a logged-in user asks is saved as a "case". A case can be marked Open or Resolved
(deviation D-01 in DEVIATIONS.md: the SRS describes query history; case status is an addition).
"""
import json

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from .db import execute, query_all, query_one
from .security import login_required

bp = Blueprint("history", __name__)

STATUSES = {"open": "Open", "resolved": "Resolved"}


def get_own_case(query_id):
    # Filtering by user_id means one user can never open another user's case (NFR-09).
    row = query_one("SELECT * FROM queries WHERE id = ? AND user_id = ?", (query_id, g.user["id"]))
    if row is None:
        abort(404, description="This case was not found in your account.")
    return row


@bp.route("/history")
@login_required
def index():
    status = request.args.get("status", "all")
    sql = ("SELECT q.id, q.query_text, q.status, q.created_at, c.name AS category_name FROM queries q "
           "LEFT JOIN categories c ON c.slug = q.category WHERE q.user_id = ?")
    params = [g.user["id"]]
    if status in STATUSES:
        sql += " AND q.status = ?"
        params.append(status)
    rows = query_all(sql + " ORDER BY q.created_at DESC, q.id DESC", params)
    return render_template("history/index.html", queries=rows, status=status, statuses=STATUSES)


@bp.route("/history/<int:query_id>")
@login_required
def detail(query_id):
    row = get_own_case(query_id)
    return render_template("history/detail.html", query=row, response=json.loads(row["response"]), statuses=STATUSES)


@bp.route("/history/<int:query_id>/status", methods=["POST"])
@login_required
def update_status(query_id):
    get_own_case(query_id)
    status = request.form.get("status", "")
    if status not in STATUSES:
        abort(400, description="Please choose a valid case status.")
    execute("UPDATE queries SET status = ? WHERE id = ? AND user_id = ?", (status, query_id, g.user["id"]))
    flash(f"Case marked as {STATUSES[status].lower()}.", "success")
    return redirect(url_for("history.detail", query_id=query_id))
