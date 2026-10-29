"""User dashboard and profile (deviation D-02 in DEVIATIONS.md: not in the SRS, added for usability, NFR-12)."""
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .auth import name_error, password_error
from .db import execute, query_all, query_one
from .security import login_required

bp = Blueprint("account", __name__)


@bp.route("/dashboard")
@login_required
def dashboard():
    user_id = g.user["id"]
    counts = query_one(
        "SELECT COUNT(*) AS total, "
        "COALESCE(SUM(status = 'open'), 0) AS open, COALESCE(SUM(status = 'resolved'), 0) AS resolved "
        "FROM queries WHERE user_id = ?",
        (user_id,),
    )
    by_category = query_all(
        "SELECT COALESCE(c.name, 'Other') AS name, COUNT(*) AS n FROM queries q "
        "LEFT JOIN categories c ON c.slug = q.category WHERE q.user_id = ? GROUP BY 1 ORDER BY n DESC, name",
        (user_id,),
    )
    recent = query_all(
        "SELECT q.id, q.query_text, q.status, q.created_at, c.name AS category_name FROM queries q "
        "LEFT JOIN categories c ON c.slug = q.category WHERE q.user_id = ? ORDER BY q.created_at DESC, q.id DESC LIMIT 5",
        (user_id,),
    )
    return render_template("account/dashboard.html", counts=counts, by_category=by_category, recent=recent)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    errors = {}
    if request.method == "POST":
        action = request.form.get("action")
        if action == "details":
            name = request.form.get("name", "").strip()
            if error := name_error(name):
                errors["name"] = error
            else:
                execute("UPDATE users SET name = ? WHERE id = ?", (name, g.user["id"]))
                flash("Your profile was updated.", "success")
                return redirect(url_for("account.profile"))
        elif action == "password":
            user = query_one("SELECT password_hash FROM users WHERE id = ?", (g.user["id"],))
            new = request.form.get("new_password", "")
            if not check_password_hash(user["password_hash"], request.form.get("current_password", "")):
                errors["current_password"] = "Your current password is incorrect."
            elif error := password_error(new):
                errors["new_password"] = error
            elif new != request.form.get("confirm_password", ""):
                errors["confirm_password"] = "Passwords do not match."
            else:
                execute("UPDATE users SET password_hash = ? WHERE id = ?", (generate_password_hash(new), g.user["id"]))
                flash("Your password was changed.", "success")
                return redirect(url_for("account.profile"))
    joined = query_one("SELECT created_at FROM users WHERE id = ?", (g.user["id"],))["created_at"]
    return render_template("account/profile.html", errors=errors, joined=joined), (400 if errors else 200)
