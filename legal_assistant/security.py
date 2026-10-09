"""Login/role checks (FR-04, NFR-07, NFR-08), CSRF protection and HTTPS/security headers (NFR-09, NFR-10)."""
import hmac
import secrets
from functools import wraps

from flask import abort, current_app, g, jsonify, redirect, request, session, url_for

from .db import query_one

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def has_page(endpoint):
    return endpoint in current_app.view_functions


def page_url(*endpoints):
    """URL of the first installed page, falling back to the home page."""
    for endpoint in endpoints:
        if has_page(endpoint):
            return url_for(endpoint)
    return url_for("query.home") if has_page("query.home") else url_for("placeholder_home")


def load_current_user():
    user_id = session.get("user_id")
    g.user = query_one("SELECT id, name, email, role FROM users WHERE id = ?", (user_id,)) if user_id else None


def _wants_json():
    return request.path.startswith("/api/")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            if _wants_json():
                return jsonify(error="Please log in to continue."), 401
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if g.user["role"] != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def check_csrf():
    if request.method not in UNSAFE_METHODS:
        return
    sent = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    if not expected or not hmac.compare_digest(sent, expected):
        abort(400, description="Your session expired. Please reload the page and try again.")


def enforce_https(app):
    if app.config["FORCE_HTTPS"] and not request.is_secure:
        return redirect(request.url.replace("http://", "https://", 1), code=301)
    return None


def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    if request.is_secure:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
    return response
