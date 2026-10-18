"""
내 원서 목록 · 상세  (담당: 성원)

쓸 수 있는 데이터는 data.py 의 APPLICATIONS 입니다.
번호를 열쇠로 하는 사전이라 data.APPLICATIONS[42] 처럼 꺼냅니다.

참고
    session.get("user_id")   지금 로그인한 사람의 번호. 로그인 안 했으면 None
    abort(403)               권한 없음
    abort(404)               없는 자원
"""
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

    return render_template("mypage/detail.html", application=application)
