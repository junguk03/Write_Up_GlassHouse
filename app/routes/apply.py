"""
원서 작성 · 합격 조회  (담당: 수하)

쓸 수 있는 데이터는 data.py 의 APPLICATIONS 입니다.
새 원서를 추가할 때는 data.next_application_id() 로 번호를 받으십시오.

원서 수정과 첨부파일 다운로드는 화면만 만들고 기능은 보류합니다.

참고
    request.form["school"]        폼에서 보낸 값 꺼내기
    request.files["document"]     첨부파일 꺼내기 (지금은 보류)
    data.APPLICATIONS[번호] = {...}   새 원서 저장
"""
from flask import (Blueprint, redirect, render_template, request, session,
                   url_for)

import data

bp = Blueprint("apply", __name__)


@bp.route("/apply", methods=["GET", "POST"])
def create():
    # TODO 1. 로그인하지 않았으면 url_for("auth.login") 으로 보낸다
    # TODO 2. POST 라면 request.form 에서 school, major, intro 를 꺼낸다
    # TODO 3. data.next_application_id() 로 새 번호를 받는다
    # TODO 4. data.APPLICATIONS 에 새 원서를 넣는다
    #         user_id 는 지금 로그인한 사람, status 는 "submitted"
    # TODO 5. url_for("mypage.list_applications") 로 보낸다
    return render_template("apply/form.html", application=None)


@bp.get("/apply/<int:app_id>/edit")
def edit(app_id):
    # 화면만 만듭니다. 기능은 보류입니다.
    return render_template("apply/form.html", application=data.APPLICATIONS.get(app_id))


@bp.get("/download")
def download():
    # 화면만 만듭니다. 기능은 보류입니다.
    return redirect(url_for("mypage.list_applications"))


@bp.get("/result")
def index():
    # TODO 1. 로그인하지 않았으면 로그인 화면으로 보낸다
    # TODO 2. 내 원서 중 status 가 accepted 또는 rejected 인 것을 모은다
    # TODO 3. applications 라는 이름으로 템플릿에 넘긴다
    return render_template("result/index.html", applications=[])
