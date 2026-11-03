import json
import os
import time
import urllib.request
import uuid

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, session, url_for)

import data
from paths import UPLOAD_DIR

bp = Blueprint("apply", __name__)

#pdf, jpg, png 만 허용
ALLOWED = (".pdf", ".jpg", ".png")
BOT_URL = os.environ.get("BOT_URL", "http://bot:5000/visit")
REVIEW_INTERVAL = 30

_last_review = {}


def request_review(app_id):
    payload = json.dumps({"app_id": app_id}).encode()
    req = urllib.request.Request(
        BOT_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5):
        pass


def store_document(file):
    name = os.path.basename(file.filename.replace("\\", "/")).strip()
    if not name:
        return None
    if not any(ext in name.lower() for ext in ALLOWED):
        return None
    stored = f"{uuid.uuid4().hex[:8]}_{name}"
    file.save(os.path.join(UPLOAD_DIR, stored))
    return stored


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

        document = None
        file = request.files.get("document")
        if file and file.filename:
            document = store_document(file)
            if document is None:
                flash("증빙서류는 PDF, JPG, PNG 파일만 올릴 수 있습니다.", "error")
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
            "document": document,
            "reason": "",
        }

        flash("원서가 제출되었습니다.", "success")
        return redirect(url_for("mypage.detail", app_id=app_id))

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
        school = request.form.get("school", "").strip()
        major = request.form.get("major", "").strip()
        intro = request.form.get("intro", "").strip()

        if not school or not major or not intro:
            flash("출신 학교, 지원 학과, 자기소개를 모두 입력해 주십시오.", "error")
            return render_template("apply/form.html", application=application)

        file = request.files.get("document")
        if file and file.filename:
            document = store_document(file)
            if document is None:
                flash("증빙서류는 PDF, JPG, PNG 파일만 올릴 수 있습니다.", "error")
                return render_template("apply/form.html", application=application)
            application["document"] = document

        application["school"] = school
        application["major"] = major
        application["intro"] = intro

        flash("원서를 수정했습니다.", "success")
        return redirect(url_for("mypage.detail", app_id=app_id))

    return render_template("apply/form.html", application=application)


@bp.post("/apply/<int:app_id>/review")
def review(app_id):
    user = data.find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("auth.login"))

    application = data.APPLICATIONS.get(app_id)
    if application is None:
        abort(404)
    if application["user_id"] != user["id"]:
        abort(403)

    waited = time.time() - _last_review.get(user["id"], 0)
    if waited < REVIEW_INTERVAL:
        flash(f"심사 요청은 {REVIEW_INTERVAL}초에 한 번만 보낼 수 있습니다. "
              f"{int(REVIEW_INTERVAL - waited)}초 뒤에 다시 시도해 주십시오.", "error")
        return redirect(url_for("mypage.detail", app_id=app_id))
    _last_review[user["id"]] = time.time()

    try:
        request_review(app_id)
        flash("심사위원에게 검토를 요청했습니다. 잠시 후 합격 조회에서 결과를 확인해 주십시오.", "success")
    except OSError:
        flash("심사위원이 다른 원서를 검토 중이거나 포털에 연결할 수 없습니다. "
              "잠시 후 다시 시도해 주십시오.", "error")

    return redirect(url_for("mypage.detail", app_id=app_id))


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
