"""AI-Based Legal Assistant, e-Lawyer and Case Guidance System.

Each feature lives in its own module/blueprint (NFR-13) so it can be changed and tested independently.
Feature modules are loaded if present, so each team member's module can be merged on its own.
"""
import importlib

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from . import db, security
from .config import Config
from .disclaimer import DISCLAIMER, SHORT_DISCLAIMER

# Module -> owner (team plan): user & case management, AI assistant, case guidance, admin.
FEATURE_MODULES = (
    "auth", "account", "history",         # Member 1
    "query",                              # Member 2 (uses Member 3 classifier/guidance/references)
    "references", "doc_templates",        # Member 3
    "feedback", "admin",                  # Member 4
)


def register_features(app):
    for name in FEATURE_MODULES:
        try:
            module = importlib.import_module(f"{__name__}.{name}")
        except ModuleNotFoundError as exc:
            if exc.name != f"{__name__}.{name}":
                raise  # the module exists but one of its own imports is missing
            continue
        app.register_blueprint(module.bp)

    if "query.home" not in app.view_functions:
        app.add_url_rule("/", "placeholder_home", lambda: render_template("placeholder.html"))


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    if app.config["FORCE_HTTPS"]:
        # Hosting platforms terminate TLS at a proxy and pass the scheme in X-Forwarded-Proto.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    db.register(app)
    register_features(app)

    @app.before_request
    def before_request():
        redirect_response = security.enforce_https(app)
        if redirect_response:
            return redirect_response
        security.load_current_user()
        security.check_csrf()
        return None

    app.after_request(security.add_security_headers)

    @app.context_processor
    def inject_globals():
        return {
            "csrf_token": security.csrf_token,
            "has_page": security.has_page,
            "home_url": security.page_url,
            "DISCLAIMER": DISCLAIMER,
            "SHORT_DISCLAIMER": SHORT_DISCLAIMER,
            "AI_ENABLED": app.config["AI_ENABLED"],
        }

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        # NFR-14: invalid input or unknown pages get a friendly message, never a stack trace.
        if request.path.startswith("/api/"):
            return jsonify(error=err.description), err.code
        return render_template("error.html", code=err.code, message=err.description), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        app.logger.exception("Unhandled error: %s", err)
        message = "Something went wrong on our side. Please try again."
        if request.path.startswith("/api/"):
            return jsonify(error=message), 500
        return render_template("error.html", code=500, message=message), 500

    return app
