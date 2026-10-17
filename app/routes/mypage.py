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
    # TODO 1. 로그인하지 않았으면 url_for("auth.login") 으로 보낸다
    # TODO 2. data.APPLICATIONS 중 user_id 가 지금 로그인한 사람과 같은 것만 모은다
    # TODO 3. 모은 목록을 applications 라는 이름으로 템플릿에 넘긴다
    return render_template("mypage/list.html", applications=[])


@bp.get("/applications/<int:app_id>")
def detail(app_id):
    # TODO 1. 로그인하지 않았으면 로그인 화면으로 보낸다
    # TODO 2. data.APPLICATIONS 에서 app_id 번 원서를 찾는다. 없으면 abort(404)
    # TODO 3. 그 원서의 user_id 가 지금 로그인한 사람과 다르면 abort(403)
    #         ← 이 검사를 빼면 IDOR 취약점이 됩니다. 지금은 넣어 둡니다.
    # TODO 4. 찾은 원서를 application 이라는 이름으로 템플릿에 넘긴다
    return render_template("mypage/detail.html", application=None)
