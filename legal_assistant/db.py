"""SQLite access, schema creation and seeding of the approved legal knowledge base."""
import json
import sqlite3
from pathlib import Path

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash

KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_all(sql, params=()):
    return get_db().execute(sql, params).fetchall()


def query_one(sql, params=()):
    return get_db().execute(sql, params).fetchone()


def execute(sql, params=()):
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    return cur.lastrowid


def _load(name):
    return json.loads((KNOWLEDGE_DIR / name).read_text(encoding="utf-8"))


def seed_knowledge(db):
    """Insert the approved categories, references and templates if the tables are empty."""
    if db.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
        for c in _load("categories.json"):
            db.execute(
                "INSERT INTO categories (slug, name, description, keywords, steps, needs_lawyer) VALUES (?, ?, ?, ?, ?, ?)",
                (c["slug"], c["name"], c["description"], c["keywords"], json.dumps(c["steps"]), c["needs_lawyer"]),
            )
    if db.execute("SELECT COUNT(*) FROM legal_references").fetchone()[0] == 0:
        for r in _load("references.json"):
            db.execute(
                "INSERT INTO legal_references (title, category, kind, source, description, url, keywords) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (r["title"], r["category"], r["kind"], r["source"], r["description"], r["url"], r.get("keywords", "")),
            )
    if db.execute("SELECT COUNT(*) FROM doc_templates").fetchone()[0] == 0:
        for t in _load("templates.json"):
            db.execute(
                "INSERT INTO doc_templates (slug, name, category, description, fields, content) VALUES (?, ?, ?, ?, ?, ?)",
                (t["slug"], t["name"], t["category"], t["description"], json.dumps(t["fields"]), t["content"]),
            )
    db.commit()


def create_admin(db, name, email, password):
    email = email.strip().lower()
    row = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if row:
        db.execute("UPDATE users SET role = 'admin' WHERE id = ?", (row[0],))
    else:
        db.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'admin')",
            (name, email, generate_password_hash(password)),
        )
    db.commit()


def migrate(db):
    """Upgrade databases created before a column was added to schema.sql."""
    columns = {row[1] for row in db.execute("PRAGMA table_info(queries)")}
    if "status" not in columns:
        db.execute("ALTER TABLE queries ADD COLUMN status TEXT NOT NULL DEFAULT 'open'")
        db.commit()


def init_db(app):
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(app.config["DATABASE"])
    try:
        db.execute("PRAGMA journal_mode = WAL")
        db.executescript((Path(__file__).resolve().parent / "schema.sql").read_text(encoding="utf-8"))
        migrate(db)
        seed_knowledge(db)
        if app.config["ADMIN_EMAIL"] and app.config["ADMIN_PASSWORD"]:
            create_admin(db, app.config["ADMIN_NAME"], app.config["ADMIN_EMAIL"], app.config["ADMIN_PASSWORD"])
    finally:
        db.close()


@click.command("create-admin")
@click.option("--name", prompt=True)
@click.option("--email", prompt=True)
@click.password_option()
def create_admin_command(name, email, password):
    """Create an administrator account (or promote an existing user)."""
    create_admin(get_db(), name, email, password)
    click.echo(f"Administrator {email} is ready.")


def register(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(create_admin_command)
    init_db(app)
