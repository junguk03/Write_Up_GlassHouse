from flask import (Blueprint, abort, redirect, render_template, session,
                   url_for)

import data

bp = Blueprint("mypage", __name__)


@bp.get("/mypage")
def list_applications():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("auth.login"))

    applications = [a for a in data.APPLICATIONS.values()
                    if a ["user_id"] == user_id]


    return render_template("mypage/list.html", applications=applications)


@bp.get("/applications/<int:app_id>")
def detail(app_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("auth.login"))
    application = data.APPLICATIONS.get(app_id)
    if application is None:
        abort(404)

    if application["user_id"] != user_id:
        abort(403)

    return render_template("mypage/detail.html", application=application)
