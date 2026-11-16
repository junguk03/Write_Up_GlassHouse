from flask import (Blueprint, abort, redirect, render_template, request,
                   url_for)

import data
import ticket

bp = Blueprint("admin", __name__)


def require_admin():
    claims = ticket.verify(request.cookies.get(ticket.COOKIE_NAME))
    if claims is None:
        return render_template("admin/denied.html"), 403
    if claims.get("role") != "staff":
        return render_template("admin/denied.html"), 403

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

    return redirect(url_for("admin.detail", app_id=app_id))


@bp.route("/admin/checkin", methods=["GET", "POST"])
def checkin():
    response = require_admin()
    if response is not None:
        return response

    result, error = None, None
    if request.method == "POST":
        token = request.form.get("ticket", "").strip()
        try:
            if token.startswith(ticket.LEGACY_PREFIX):
                guest = ticket.read_legacy(token)
            else:
                guest = ticket.verify(token)
        except Exception:
            guest = None
        if guest is None:
            error = "확인할 수 없는 초대권입니다."
        else:
            result = guest.get("name") if isinstance(guest, dict) else guest

    return render_template("admin/checkin.html", result=result, error=error)
