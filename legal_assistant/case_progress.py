
"""Case progress tracking and document checklist for Issue #49."""

import json

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from .db import execute, query_all, query_one
from .security import login_required

bp = Blueprint("case_progress", __name__, url_prefix="/cases")


def get_owned_case(query_id):
    """Return a case only when it belongs to the logged-in user."""
    case = query_one(
        "SELECT id, user_id, query_text, category, response, status, created_at "
        "FROM queries WHERE id = ? AND user_id = ?",
        (query_id, g.user["id"]),
    )
    if case is None:
        abort(404)
    return case


def get_steps(case):
    """Read procedure steps saved in the original query response."""
    try:
        response = json.loads(case["response"])
        steps = response.get("steps", [])
        return steps if isinstance(steps, list) else []
    except (TypeError, json.JSONDecodeError):
        return []


def get_documents(case):
    """Build a basic document checklist for the case category."""
    category = case["category"]

    defaults = {
        "consumer": [
            "Bill or purchase invoice",
            "Order details and warranty card",
            "Photos of the defect or problem",
            "Messages or emails with the seller",
        ],
        "property": [
            "Rent or lease agreement",
            "Rent receipts or payment proof",
            "Messages with the landlord or other party",
        ],
        "family": [
            "Relevant marriage or family documents",
            "Financial records, if relevant",
            "Relevant messages or other supporting evidence",
        ],
        "criminal": [
            "Written complaint or FIR copy, if available",
            "Photos, messages or other evidence",
            "Relevant transaction or incident records",
        ],
        "employment": [
            "Appointment or employment letter",
            "Salary slips and bank statements",
            "Relevant emails or written communication",
        ],
        "cyber": [
            "Transaction ID or bank statement, if relevant",
            "Screenshots and messages",
            "Complaint acknowledgement, if available",
        ],
        "rti": [
            "Copy of the RTI application",
            "Fee payment proof, if applicable",
            "Reply or appeal documents, if available",
        ],
    }

    return defaults.get(category, [
        "Relevant supporting documents",
        "Copies of important messages or correspondence",
        "Any complaint or application acknowledgement",
    ])


def save_checklist(query_id, item_type, item_key, completed):
    """Insert or update one checklist item."""
    if item_type == "step":
        execute(
            """
            INSERT INTO case_step_progress
                (query_id, step_index, completed, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(query_id, step_index)
            DO UPDATE SET completed = excluded.completed,
                          updated_at = datetime('now')
            """,
            (query_id, int(item_key), int(completed)),
        )
    else:
        execute(
            """
            INSERT INTO case_documents
                (query_id, document_name, prepared, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(query_id, document_name)
            DO UPDATE SET prepared = excluded.prepared,
                          updated_at = datetime('now')
            """,
            (query_id, item_key, int(completed)),
        )


@bp.route("/")
@login_required
def index():
    """List the current user's saved cases."""
    cases = query_all(
        "SELECT id, query_text, category, status, created_at "
        "FROM queries WHERE user_id = ? ORDER BY created_at DESC, id DESC",
        (g.user["id"],),
    )
    return render_template("case_progress/index.html", cases=cases)


@bp.route("/<int:query_id>/progress")
@login_required
def progress(query_id):
    """Show procedure progress and document checklist for one case."""
    case = get_owned_case(query_id)
    steps = get_steps(case)
    documents = get_documents(case)

    step_rows = {
        row["step_index"]: row["completed"]
        for row in query_all(
            "SELECT step_index, completed FROM case_step_progress WHERE query_id = ?",
            (query_id,),
        )
    }
    document_rows = {
        row["document_name"]: row["prepared"]
        for row in query_all(
            "SELECT document_name, prepared FROM case_documents WHERE query_id = ?",
            (query_id,),
        )
    }

    progress_steps = [
        {"index": i, "text": text, "completed": bool(step_rows.get(i, 0))}
        for i, text in enumerate(steps)
    ]
    progress_documents = [
        {"name": name, "prepared": bool(document_rows.get(name, 0))}
        for name in documents
    ]

    completed_steps = sum(item["completed"] for item in progress_steps)
    completed_documents = sum(item["prepared"] for item in progress_documents)

    return render_template(
        "case_progress/progress.html",
        case=case,
        steps=progress_steps,
        documents=progress_documents,
        completed_steps=completed_steps,
        total_steps=len(progress_steps),
        completed_documents=completed_documents,
        total_documents=len(progress_documents),
    )


@bp.route("/<int:query_id>/progress", methods=["POST"])
@login_required
def update_progress(query_id):
    """Save one step or document checkbox."""
    case = get_owned_case(query_id)
    item_type = request.form.get("item_type", "")
    completed = request.form.get("completed") == "1"

    if item_type == "step":
        try:
            index = int(request.form.get("item_key", ""))
        except (TypeError, ValueError):
            abort(400)

        steps = get_steps(case)
        if index < 0 or index >= len(steps):
            abort(400)

        save_checklist(query_id, "step", index, completed)

    elif item_type == "document":
        item_key = request.form.get("item_key", "")
        if item_key not in get_documents(case):
            abort(400)
        save_checklist(query_id, "document", item_key, completed)

    else:
        abort(400)

    flash("Case progress saved.", "success")
    return redirect(url_for("case_progress.progress", query_id=query_id))
