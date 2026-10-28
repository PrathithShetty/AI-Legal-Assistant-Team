"""User registration, login and logout (FR-01 to FR-03, NFR-11)."""
import re
import sqlite3

from flask import Blueprint, flash, g, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from .db import execute, query_one
from .security import page_url

bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


def name_error(name):
    if not 2 <= len(name.strip()) <= 80:
        return "Please enter your name (2 to 80 characters)."
    return None


def password_error(password):
    if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must be at least 8 characters and include a letter and a number."
    return None


def validate_registration(form):
    """Return a dict of field -> error message (FR-02). Empty dict means the input is valid."""
    errors = {}
    email = form.get("email", "").strip()
    password = form.get("password", "")

    if error := name_error(form.get("name", "")):
        errors["name"] = error
    if not EMAIL_RE.match(email) or len(email) > 254:
        errors["email"] = "Please enter a valid email address."
    if error := password_error(password):
        errors["password"] = error
    if password != form.get("confirm_password", ""):
        errors["confirm_password"] = "Passwords do not match."
    if form.get("accept_disclaimer") != "on":
        errors["accept_disclaimer"] = "Please confirm that you understand this is not legal advice."
    return errors


def _safe_next(target):
    return target if target and target.startswith("/") and not target.startswith("//") else page_url("account.dashboard")


def _start_session(user_id):
    session.clear()  # prevents session fixation
    session["user_id"] = user_id


@bp.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(page_url())
    errors, form = {}, {}
    if request.method == "POST":
        form = request.form
        errors = validate_registration(form)
        if not errors:
            try:
                user_id = execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (form["name"].strip(), form["email"].strip().lower(), generate_password_hash(form["password"])),
                )
            except sqlite3.IntegrityError:
                errors["email"] = "An account with this email already exists. Please log in."
            else:
                _start_session(user_id)
                flash("Welcome! Your account has been created.", "success")
                return redirect(page_url())
    return render_template("auth/register.html", errors=errors, form=form), (400 if errors else 200)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(page_url())
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = query_one("SELECT id, password_hash FROM users WHERE email = ?", (email,))
        if user and check_password_hash(user["password_hash"], request.form.get("password", "")):
            _start_session(user["id"])
            return redirect(_safe_next(request.args.get("next")))
        # Same message for unknown email and wrong password, so accounts cannot be guessed.
        error = "Incorrect email or password."
    return render_template("auth/login.html", error=error), (401 if error else 200)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(page_url())
