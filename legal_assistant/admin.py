"""Administrator dashboard (FR-23; FR-24 and FR-25 follow in Sprint 2). Every route requires the admin role (FR-04, NFR-08, BR-04)."""
import json
import re
import sqlite3
from dataclasses import dataclass, field

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .db import execute, query_all, query_one
from .security import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REFERENCE_KINDS = ["Act", "Rules", "Case", "Guideline", "Model Law"]


@dataclass
class Field:
    name: str
    label: str
    kind: str = "text"            # text | textarea | lines | checkbox | select | json | url | slug
    required: bool = True
    max_length: int = 5000
    options: list = field(default_factory=list)
    help: str = ""


@dataclass
class Entity:
    table: str
    title: str
    singular: str
    list_columns: list
    fields: list
    summary: str = ""            # shown on the admin dashboard after the item count
    order_by: str = "id"


def category_options():
    return [("general", "General")] + [(r["slug"], r["name"]) for r in query_all("SELECT slug, name FROM categories ORDER BY name")]


ENTITIES = {
    "categories": Entity(
        table="categories", title="Approved legal information", singular="category", order_by="name",
        summary="categories with descriptions, classification keywords and procedure steps.",
        list_columns=[("name", "Name"), ("slug", "Slug"), ("updated_at", "Last updated")],
        fields=[
            Field("slug", "Slug (unique short id)", "slug", max_length=40, help="Lowercase letters, numbers and hyphens."),
            Field("name", "Name", max_length=100),
            Field("description", "Description shown to users", "textarea", max_length=1000),
            Field("keywords", "Classification keywords", "textarea", max_length=3000, help="Comma separated. Phrases with spaces score higher."),
            Field("steps", "Procedure steps", "lines", max_length=5000, help="One step per line."),
            Field("needs_lawyer", "Always recommend consulting a lawyer for this category", "checkbox", required=False),
        ],
    ),
}


def get_entity(name):
    entity = ENTITIES.get(name)
    if entity is None:
        abort(404)
    return entity


def display_value(f, row):
    """Convert a stored value into what the form shows."""
    if row is None:
        return ""
    value = row[f.name]
    if f.kind == "lines":
        return "\n".join(json.loads(value))
    if f.kind == "json":
        return json.dumps(json.loads(value), indent=2)
    return value


def parse_form(entity, form):
    """Validate the submitted form. Returns (values to store, raw values for redisplay, errors)."""
    values, raw, errors = {}, {}, {}
    for f in entity.fields:
        if f.kind == "checkbox":
            values[f.name] = 1 if form.get(f.name) == "on" else 0
            raw[f.name] = values[f.name]
            continue
        text = form.get(f.name, "").strip()
        raw[f.name] = text
        if f.required and not text:
            errors[f.name] = "This field is required."
            continue
        if len(text) > f.max_length:
            errors[f.name] = f"Please keep this under {f.max_length} characters."
            continue
        if f.kind == "slug" and not SLUG_RE.match(text):
            errors[f.name] = "Use lowercase letters, numbers and single hyphens only."
        elif f.kind == "url" and text and not text.startswith(("https://", "http://")):
            errors[f.name] = "Links must start with https:// or http://."
        elif f.kind == "select":
            allowed = [o[0] for o in (f.options or category_options())]
            if text not in allowed:
                errors[f.name] = "Please choose a valid option."
        elif f.kind == "lines":
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = json.dumps(lines)
        elif f.kind == "json":
            error = validate_template_fields(text)
            if error:
                errors[f.name] = error
        values[f.name] = text
    return values, raw, errors


def validate_template_fields(text):
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return f"Invalid JSON: {exc.msg} (line {exc.lineno})."
    if not isinstance(data, list) or not data:
        return "Fields must be a non-empty list."
    for item in data:
        if not isinstance(item, dict) or not re.fullmatch(r"\w+", str(item.get("name", ""))) or not item.get("label"):
            return 'Each field needs a "name" (letters, numbers, underscore) and a "label".'
        if item.get("type", "text") not in ("text", "textarea", "date"):
            return 'Field "type" must be text, textarea or date.'
    return None


@bp.route("/")
@admin_required
def dashboard():
    counts = {name: query_one(f"SELECT COUNT(*) AS n FROM {e.table}")["n"] for name, e in ENTITIES.items()}
    counts.update(
        feedback_new=query_one("SELECT COUNT(*) AS n FROM feedback WHERE reviewed = 0")["n"],
        users=query_one("SELECT COUNT(*) AS n FROM users")["n"],
        queries=query_one("SELECT COUNT(*) AS n FROM queries")["n"],
    )
    return render_template("admin/dashboard.html", counts=counts, entities=ENTITIES)


@bp.route("/<entity_name>")
@admin_required
def entity_list(entity_name):
    entity = get_entity(entity_name)
    rows = query_all(f"SELECT * FROM {entity.table} ORDER BY {entity.order_by}")
    return render_template("admin/list.html", entity=entity, entity_name=entity_name, rows=rows)


@bp.route("/<entity_name>/new", methods=["GET", "POST"])
@bp.route("/<entity_name>/<int:item_id>/edit", methods=["GET", "POST"])
@admin_required
def entity_form(entity_name, item_id=None):
    entity = get_entity(entity_name)
    row = None
    if item_id is not None:
        row = query_one(f"SELECT * FROM {entity.table} WHERE id = ?", (item_id,))
        if row is None:
            abort(404)

    errors = {}
    values = {f.name: display_value(f, row) for f in entity.fields}
    if request.method == "POST":
        data, values, errors = parse_form(entity, request.form)
        if not errors:
            columns = list(data)
            try:
                if row is None:
                    execute(f"INSERT INTO {entity.table} ({', '.join(columns)}) VALUES ({', '.join('?' * len(columns))})",
                            [data[c] for c in columns])
                else:
                    assignments = ", ".join(f"{c} = ?" for c in columns)
                    if entity.table == "categories":
                        assignments += ", updated_at = datetime('now')"
                    execute(f"UPDATE {entity.table} SET {assignments} WHERE id = ?", [data[c] for c in columns] + [item_id])
            except sqlite3.IntegrityError:
                errors["slug"] = "This slug is already used. Please choose another."
            else:
                flash(f"The {entity.singular} was saved.", "success")
                return redirect(url_for("admin.entity_list", entity_name=entity_name))

    return render_template(
        "admin/form.html", entity=entity, entity_name=entity_name, row=row, values=values, errors=errors,
        category_options=category_options(),
    ), (400 if errors else 200)


@bp.route("/<entity_name>/<int:item_id>/delete", methods=["POST"])
@admin_required
def entity_delete(entity_name, item_id):
    entity = get_entity(entity_name)
    execute(f"DELETE FROM {entity.table} WHERE id = ?", (item_id,))
    flash(f"The {entity.singular} was deleted.", "info")
    return redirect(url_for("admin.entity_list", entity_name=entity_name))
