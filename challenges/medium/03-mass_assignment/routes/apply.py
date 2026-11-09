from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, session, url_for)

import data

bp = Blueprint("apply", __name__)


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
            "status": "rejected",
        }

        flash("원서가 제출되었습니다.", "success")
        return redirect(url_for("mypage.list_applications"))

    return render_template("apply/form.html", application=None)


@bp.route("/apply/<int:app_id>/edit", methods=["GET", "POST"])
def edit(app_id):

    user = data.find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("auth.login"))

    application = data.APPLICATIONS.get(app_id)
    if application is None:
        abort(404)
    if application["user_id"] != user["id"]:
        abort(403)

    if request.method == "POST":
        for key in request.form:
            application[key] = request.form[key]
        if application["status"] == "accepted":
            flash("합격 인증 코드 " + current_app.config["FLAG_PROMOTED"], "success")
        return redirect(url_for("mypage.list_applications"))

    return render_template("apply/form.html", application=application)


@bp.get("/download")
def download():
    return redirect(url_for("mypage.list_applications"))


@bp.get("/result")
def index():
    exam_no = request.args.get("exam_no", "")
    application = data.APPLICATIONS.get(int(exam_no)) if exam_no.isdigit() else None
    return render_template("result/index.html", application=application)
