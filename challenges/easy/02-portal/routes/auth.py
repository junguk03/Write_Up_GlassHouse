import base64
import json

import re

from flask import (Blueprint, flash, make_response, redirect, render_template,
                   request, session, url_for)

import data

bp = Blueprint("auth", __name__)


def make_auth_cookie(user):
    info = {"user": user["id"], "role": user["role"]}
    return base64.b64encode(json.dumps(info).encode()).decode()


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","")
        password = request.form.get("password","")

        user = data.USERS.get(username)

        if user is None or user["password"] != password:
            flash("아이디 또는 비밀번호가 올바르지 않습니다.","error")
            return render_template("auth/login.html")

        session["user_id"] = user["id"]
        session["role"] = user["role"]
        resp = make_response(redirect(url_for("mypage.list_applications")))
        resp.set_cookie("gh_8002_auth", make_auth_cookie(user))
        return resp

    return render_template("auth/login.html")


@bp.get("/logout")
def logout():
    session.clear()
    resp = make_response(redirect(url_for("main.index")))
    resp.delete_cookie("gh_8002_auth")
    return resp


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        form = {"username": username, "name": name, "email": email}

        if not re.fullmatch(r"[A-Za-z0-9]{4,20}", username):
            flash("아이디는 영문과 숫자 4~20자로 입력해 주십시오.", "error")
            return render_template("auth/signup.html", form=form)
        if username in data.USERS:
            flash("이미 사용 중인 아이디입니다.", "error")
            return render_template("auth/signup.html", form=form)
        if not password or password != request.form.get("password_confirm", ""):
            flash("비밀번호가 비어 있거나 서로 다릅니다.", "error")
            return render_template("auth/signup.html", form=form)
        if not name or not email:
            flash("이름과 이메일을 모두 입력해 주십시오.", "error")
            return render_template("auth/signup.html", form=form)

        data.USERS[username] = {
            "id": data.next_user_id(),
            "password": password,
            "name": name,
            "role": "applicant",
            "email": email,
        }
        flash("가입되었습니다. 로그인해 주십시오.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html", form={})

