import secrets

from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)

import data

bp = Blueprint("auth", __name__)

RESET_CODES = {}
MAX_TRIES = 5


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
        return redirect(url_for("mypage.list_applications"))

    return render_template("auth/login.html")


@bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))


@bp.get("/signup")
def signup():
    return render_template("auth/signup.html")


@bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        username = request.form.get("username", "")
        email = request.form.get("email", "")
        user = data.USERS.get(username)

        if user is None or user["email"] != email:
            flash("아이디 또는 이메일이 올바르지 않습니다.", "error")
            return render_template("auth/forgot.html")

        code = f"{secrets.randbelow(1_000_000):06d}"
        RESET_CODES[username] = {"code": code, "tries": 0}

        print(f"[비밀번호 찾기] {username} 인증코드 {code}", flush=True)

        session["reset_user"] = username
        session.pop("reset_verified", None)
        flash("등록된 이메일로 인증코드를 보냈습니다.", "info")
        return redirect(url_for("auth.verify"))

    return render_template("auth/forgot.html")


@bp.route("/forgot/verify", methods=["GET", "POST"])
def verify():
    username = session.get("reset_user")
    pending = RESET_CODES.get(username)
    if pending is None:
        flash("비밀번호 찾기를 처음부터 다시 진행해 주십시오.", "error")
        return redirect(url_for("auth.forgot"))

    if request.method == "POST":
        if request.form.get("code", "") != pending["code"]:
            pending["tries"] += 1
            if pending["tries"] >= MAX_TRIES:
                del RESET_CODES[username]
                flash(f"{MAX_TRIES}회 틀려 인증이 취소되었습니다. 처음부터 다시 진행해 주십시오.", "error")
                return redirect(url_for("auth.forgot"))
            flash(f"인증코드가 올바르지 않습니다. ({pending['tries']}/{MAX_TRIES})", "error")
            return render_template("auth/verify.html")

        del RESET_CODES[username]
        session["reset_verified"] = True
        return redirect(url_for("auth.reset"))

    return render_template("auth/verify.html")


@bp.route("/forgot/reset", methods=["GET", "POST"])
def reset():
    username = session.get("reset_user")
    if username is None :
        flash("본인 확인을 먼저 진행해 주십시오.", "error")
        return redirect(url_for("auth.forgot"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if not password or password != request.form.get("password_confirm", ""):
            flash("비밀번호가 비어 있거나 서로 다릅니다.", "error")
            return render_template("auth/reset.html")

        data.USERS[username]["password"] = password
        session.pop("reset_user", None)
        session.pop("reset_verified", None)
        flash("비밀번호를 바꿨습니다. 새 비밀번호로 로그인해 주십시오.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset.html")
