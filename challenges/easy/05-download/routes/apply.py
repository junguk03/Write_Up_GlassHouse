import os

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, send_file, session, url_for)

import data

bp = Blueprint("apply", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


@bp.route("/apply", methods=["GET", "POST"])
def create():
    user = data.find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        school = request.form.get("school", "").strip()
        major = request.form.get("major", "").strip()
        intro = request.form.get("intro", "").strip()

        if not school or not major or not intro:
            flash("출신 학교, 지원 학과, 자기소개를 모두 입력해 주십시오.", "error")
            return render_template("apply/form.html", application=None)

        app_id = data.next_application_id()

        data.APPLICATIONS[app_id] = {
            "id": app_id,
            "user_id": user["id"],
            "applicant_name": user["name"],
            "school": school,
            "major": major,
            "intro": intro,
            "status": "submitted",
        }

        flash("원서가 제출되었습니다.", "success")
        return redirect(url_for("mypage.list_applications"))

    return render_template("apply/form.html", application=None)


@bp.get("/apply/<int:app_id>/edit")
def edit(app_id):
    user = data.find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("auth.login"))

    application = data.APPLICATIONS.get(app_id)
    if application is None:
        abort(404)
    if application["user_id"] != user["id"]:
        abort(403)

    return render_template("apply/form.html", application=application)


@bp.get("/download")
def download():
    # 보관함에서 요청한 파일을 꺼내 내려 준다.
    filename = request.args.get("file", "")
    filename = filename.replace("../", "")
    target = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(target):
        abort(404)
    return send_file(target)


@bp.get("/result")
def index():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("auth.login"))

    applications = [
        a for a in data.APPLICATIONS.values()
        if a["user_id"] == user_id and a["status"] in ("accepted", "rejected")
    ]

    return render_template("result/index.html", applications=applications)
