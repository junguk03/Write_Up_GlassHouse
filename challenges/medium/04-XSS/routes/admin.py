import os

from flask import (Blueprint, abort, redirect, render_template, request,
                   send_file, session, url_for)

import data
from paths import ARCHIVE_DIR

bp = Blueprint("admin", __name__)


def require_admin():
    role = session.get("role")
    if role is None:
        return redirect(url_for("auth.login"))
    if role != "admin":
        abort(403)
    return None


@bp.get("/admin")
def index():
    response = require_admin()
    if response is not None:
        return response
    applications = list(data.APPLICATIONS.values())
    return render_template("admin/list.html", applications=applications)


@bp.get("/admin/applications/<int:app_id>")
def detail(app_id):
    response = require_admin()
    if response is not None:
        return response

    application = data.APPLICATIONS.get(app_id)
    if application is None:
        abort(404)

    return render_template("admin/detail.html", application=application)


@bp.get("/admin/archive")
def archive():
    response = require_admin()
    if response is not None:
        return response

    name = request.args.get("name", "")
    if not name:
        abort(404)

    path = os.path.join(ARCHIVE_DIR, name)
    if not os.path.isfile(path):
        abort(404)

    return send_file(path, mimetype="text/plain")


@bp.post("/admin/applications/<int:app_id>/decide")
def decide(app_id):
    response = require_admin()
    if response is not None:
        return response

    application = data.APPLICATIONS.get(app_id)
    if application is None:
        abort(404)

    decision = request.form.get("decision")
    if decision not in ("accepted", "rejected"):
        abort(400)

    application["status"] = decision
    application["reason"] = request.form.get("reason", "")

    return redirect(url_for("admin.detail", app_id=app_id))
