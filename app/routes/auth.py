"""
로그인 · 로그아웃 · 회원가입 화면  (담당: 성원)

구현해야 할 것은 아래 TODO 에 적어 두었습니다.
쓸 수 있는 데이터는 data.py 의 USERS 입니다.

참고
    request.form["username"]   폼에서 보낸 값 꺼내기
    session["user_id"] = 1     로그인 상태 기록하기
    session.clear()            로그아웃
    flash("메시지", "error")   화면에 알림 띄우기 (base.html 이 받아서 보여줍니다)
    redirect(url_for("main.index"))   다른 화면으로 보내기
"""
from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)

import data

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # TODO 1. request.form 에서 username 과 password 를 꺼낸다
        # TODO 2. data.USERS 에서 그 아이디를 찾는다
        # TODO 3. 없거나 비밀번호가 다르면
        #         flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error") 후
        #         다시 로그인 화면을 보여준다
        # TODO 4. 맞으면 session["user_id"] 와 session["role"] 에 값을 넣고
        #         url_for("mypage.list_applications") 로 보낸다
        pass

    return render_template("auth/login.html")


@bp.get("/logout")
def logout():
    # TODO. session 을 비우고 메인으로 보낸다
    return redirect(url_for("main.index"))


@bp.get("/signup")
def signup():
    # 회원가입은 화면만 만듭니다. 기능은 보류입니다.
    return render_template("auth/signup.html")
