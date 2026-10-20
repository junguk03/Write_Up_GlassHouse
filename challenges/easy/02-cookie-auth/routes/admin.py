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
import base64
import json

from flask import (Blueprint, abort, redirect, render_template, request,
                   session, url_for)

import data

bp = Blueprint("admin", __name__)


def require_admin():
    """관리자가 아니면 막습니다. 각 함수 맨 위에서 부르십시오.

    로그인할 때 심어 둔 auth 쿠키를 읽어 권한을 확인합니다.
    쿠키 값은 사용자 정보를 base64 로 담고 있어, 서버는 그걸 그대로 신뢰합니다.
    """
    raw = request.cookies.get("auth")
    # 쿠키가 없으면 로그인하지 않은 것으로 봅니다
    if not raw:
        return redirect(url_for("auth.login"))

    # auth 쿠키를 풀어 사용자 정보를 읽습니다
    try:
        info = json.loads(base64.b64decode(raw).decode())
    except Exception:
        return redirect(url_for("auth.login"))

    # 쿠키에 적힌 role 이 admin 이면 통과시킵니다
    if info.get("role") != "admin":
        abort(403)

    return None


@bp.get("/admin")
def index():
    response = require_admin()
    if response is not None:
        return response
    # TODO. data.APPLICATIONS 전체를 목록으로 만들어 템플릿에 넘긴다
    #       관리자는 모든 원서를 볼 수 있으므로 거르지 않습니다
    applications = list(data.APPLICATIONS.values())
    return render_template("admin/list.html", applications=applications)


@bp.get("/admin/applications/<int:app_id>")
def detail(app_id):
    response = require_admin()
    if response is not None:
        return response
    # TODO. app_id 번 원서를 찾아 템플릿에 넘긴다. 없으면 abort(404)
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
    # TODO 1. request.form["decision"] 을 꺼낸다 ("accepted" 또는 "rejected")
    decision = request.form.get("decision")
    if decision not in ("accepted", "rejected"):
        abort(400)
    # TODO 2. data.APPLICATIONS[app_id]["status"] 를 그 값으로 바꾼다
    application["status"] = decision
    # TODO 3. url_for("admin.detail", app_id=app_id) 로 돌려보낸다

    return redirect(url_for("admin.detail", app_id=app_id))
