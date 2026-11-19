"""
신청서 작성 · 당첨 조회 · 확인서류 미리보기
"""
import os

import requests

import ipaddress
import socket
from urllib.parse import urlparse

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, send_file, session, url_for)

import data

bp = Blueprint("apply", __name__)

UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads"
)


def save_document(file):
    if not file or not file.filename:
        return None

    name = os.path.basename(file.filename)
    ext = os.path.splitext(name)[1].lower()
    allowed_ext = (".pdf", ".png", ".jpg", ".jpeg")
    allowed_mime = ("application/pdf", "image/png", "image/jpeg")

    if ext not in allowed_ext or file.mimetype not in allowed_mime:
        return None

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file.save(os.path.join(UPLOAD_DIR, name))
    return name

@bp.route("/apply", methods=["GET", "POST"])
def create():
    user = data.find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        school = request.form.get("school", "").strip()
        major = request.form.get("major", "").strip()
        intro = request.form.get("intro", "").strip()
        portfolio_url = request.form.get("portfolio_url", "").strip()

        if not school or not major or not intro:
            flash("소속, 희망 좌석, 신청 사연을 모두 입력해 주십시오.", "error")
            return render_template("apply/form.html", application=None)

        document = save_document(request.files.get("document"))

        app_id = data.next_application_id()
        data.APPLICATIONS[app_id] = {
            "id": app_id,
            "user_id": user["id"],
            "applicant_name": user["name"],
            "school": school,
            "major": major,
            "intro": intro,
            "portfolio_url": portfolio_url,
            "document": document,
            "status": "submitted",
        }

        flash("신청서가 제출되었습니다.", "success")
        return redirect(url_for("mypage.list_applications"))

    return render_template("apply/form.html", application=None)

def _is_blocked(url):
    host = urlparse(url).hostname
    if not host:
        return True
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(host))
    except OSError:
        return True
    if ip.is_loopback:
        return True
    try:
        converter_ip = ipaddress.ip_address(socket.gethostbyname("converter"))
    except OSError:
        return False
    return ip == converter_ip        # converter 주소면 차단

@bp.get("/preview")
def preview():
    user = data.find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("auth.login"))

    url = request.args.get("url", "").strip()
    result = None

    if url:
        if _is_blocked(url):
            result = "내부 주소에는 접근할 수 없습니다."
        else:
            r = requests.get(url, timeout=3)
            result = r.text[:500]

    return render_template("apply/preview.html", url=url, result=result)


@bp.get("/uploads/<path:name>")
def uploaded(name):
    # 올린 확인서류를 다시 볼 수 있게 내려 줍니다. 경로 이탈만 막습니다.
    if name.startswith("/") or ".." in name:
        abort(400)
    path = os.path.join(UPLOAD_DIR, name)
    if not os.path.isfile(path):
        abort(404)
    return send_file(path)


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
