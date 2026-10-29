"""Legal document templates: list, explain and generate (FR-17 to FR-19)."""
import json
import re

from flask import Blueprint, abort, render_template, request

from .db import query_all, query_one

bp = Blueprint("doc_templates", __name__)

PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")
MAX_FIELD_LENGTH = 3000


def fill_template(content, fields, values):
    """Replace {{field}} placeholders. Empty fields stay visible as [Field label] so users can fill them by hand."""
    labels = {f["name"]: f["label"] for f in fields}

    def replace(match):
        name = match.group(1)
        value = (values.get(name) or "").strip()[:MAX_FIELD_LENGTH]
        return value or f"[{labels.get(name, name)}]"

    return PLACEHOLDER.sub(replace, content)


def get_template(slug):
    row = query_one("SELECT * FROM doc_templates WHERE slug = ?", (slug,))
    if row is None:
        abort(404, description="This template was not found.")
    return row


@bp.route("/templates")
def index():
    rows = query_all(
        "SELECT t.*, COALESCE(c.name, 'General') AS category_name FROM doc_templates t "
        "LEFT JOIN categories c ON c.slug = t.category ORDER BY category_name, t.name"
    )
    return render_template("templates/index.html", templates=rows)


@bp.route("/templates/<slug>", methods=["GET", "POST"])
def detail(slug):
    row = get_template(slug)
    fields = json.loads(row["fields"])
    values = request.form if request.method == "POST" else {}
    document = fill_template(row["content"], fields, values)
    return render_template(
        "templates/detail.html", template=row, fields=fields, values=values, document=document,
        generated=request.method == "POST",
    )
