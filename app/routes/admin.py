"""
심사위원 포털  (담당: 종성)

지원자 목록, 원서 상세(심사), 합격 · 불합격 처리를 담당합니다.
쓸 수 있는 데이터는 data.py 의 APPLICATIONS 입니다.

관리자 계정은 reviewer / adminpw 입니다.
화면을 확인할 때는 /dev/login-as/reviewer 로 들어가면 바로 관리자가 됩니다.

참고
    session.get("role")    "applicant" 또는 "admin"
    abort(403)             권한 없음
"""
from flask import (Blueprint, abort, redirect, render_template, request,
                   session, url_for)

import data

bp = Blueprint("admin", __name__)


def require_admin():
    """관리자가 아니면 막습니다. 각 함수 맨 위에서 부르십시오."""
    # TODO 1. 로그인하지 않았으면 url_for("auth.login") 으로 보낼 수 있게 처리한다
    # TODO 2. session.get("role") 이 "admin" 이 아니면 abort(403)
    #         ← 이 검사를 빼면 Broken Access Control 취약점이 됩니다. 지금은 넣어 둡니다.
    pass


@bp.get("/admin")
def index():
    require_admin()
    # TODO. data.APPLICATIONS 전체를 목록으로 만들어 템플릿에 넘긴다
    #       관리자는 모든 원서를 볼 수 있으므로 거르지 않습니다
    return render_template("admin/list.html", applications=[])


@bp.get("/admin/applications/<int:app_id>")
def detail(app_id):
    require_admin()
    # TODO. app_id 번 원서를 찾아 템플릿에 넘긴다. 없으면 abort(404)
    return render_template("admin/detail.html", application=None)


@bp.post("/admin/applications/<int:app_id>/decide")
def decide(app_id):
    require_admin()
    # TODO 1. request.form["decision"] 을 꺼낸다 ("accepted" 또는 "rejected")
    # TODO 2. data.APPLICATIONS[app_id]["status"] 를 그 값으로 바꾼다
    # TODO 3. url_for("admin.detail", app_id=app_id) 로 돌려보낸다
    return redirect(url_for("admin.index"))
