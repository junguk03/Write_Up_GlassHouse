import base64
import json

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
        resp.set_cookie("auth", make_auth_cookie(user))
        return resp

    return render_template("auth/login.html")


@bp.get("/logout")
def logout():
    session.clear()
    resp = make_response(redirect(url_for("main.index")))
    resp.delete_cookie("auth")
    return resp


@bp.get("/signup")
def signup():
    return render_template("auth/signup.html")
