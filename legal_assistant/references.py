"""Legal references and case law (FR-14 to FR-16)."""
from flask import Blueprint, render_template, request

from .classifier import score
from .db import query_all

bp = Blueprint("references", __name__)

NO_REFERENCE_MESSAGE = "No suitable legal reference was found for this question in our approved sources."


def to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "kind": row["kind"],
        "source": row["source"],
        "description": row["description"],
        "url": row["url"],
        "category": row["category"],
    }


def find_references(category_slug, text, limit=4):
    """Return the most relevant approved references for a classified query (FR-14).

    Only references stored in the database are returned, so the system never invents a citation (FR-16).
    """
    if not category_slug:
        return []
    rows = query_all("SELECT * FROM legal_references WHERE category = ? ORDER BY id", (category_slug,))
    # Stable sort: references with equal relevance keep their seeded order (main Act first).
    ranked = sorted(rows, key=lambda r: score(text, r["keywords"]), reverse=True)
    return [to_dict(r) for r in ranked[:limit]]


@bp.route("/references")
def index():
    category = request.args.get("category", "")
    search = request.args.get("q", "").strip()
    sql = "SELECT r.*, COALESCE(c.name, 'General') AS category_name FROM legal_references r " \
          "LEFT JOIN categories c ON c.slug = r.category WHERE 1 = 1"
    params = []
    if category:
        sql += " AND r.category = ?"
        params.append(category)
    if search:
        sql += " AND (r.title LIKE ? OR r.description LIKE ? OR r.keywords LIKE ?)"
        params += [f"%{search}%"] * 3
    sql += " ORDER BY category_name, r.kind, r.title"
    rows = query_all(sql, params)
    categories = query_all("SELECT slug, name FROM categories ORDER BY name")
    return render_template(
        "references.html", references=rows, categories=categories, selected=category, search=search,
        no_reference_message=NO_REFERENCE_MESSAGE,
    )
