"""
로그인 · 로그아웃 · 회원가입 · 비밀번호 찾기 화면  (담당: 성원)

구현해야 할 것은 아래 TODO 에 적어 두었습니다.
쓸 수 있는 데이터는 data.py 의 USERS 입니다.

참고
    request.form["username"]   폼에서 보낸 값 꺼내기
    session["user_id"] = 1     로그인 상태 기록하기
    session.clear()            로그아웃
    flash("메시지", "error")   화면에 알림 띄우기 (base.html 이 받아서 보여줍니다)
    redirect(url_for("main.index"))   다른 화면으로 보내기

비밀번호 찾기는 세 단계입니다. 앞 단계를 통과해야 다음 화면이 열립니다.
    /forgot          아이디 + 이메일 확인   → session["reset_user"]
    /forgot/verify   인증코드 확인          → session["reset_verified"]
    /forgot/reset    새 비밀번호 저장       (위 두 값을 모두 확인)
"""
import secrets

from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)

import data

bp = Blueprint("auth", __name__)

# 비밀번호 찾기 인증코드는 서버 메모리에 둡니다.
# 세션 쿠키는 서명만 될 뿐 암호화되지 않아 사용자가 풀어 볼 수 있으므로,
# 코드를 세션에 넣으면 그대로 노출됩니다.
#   키 = 아이디,  값 = {"code": "042719", "tries": 0}
RESET_CODES = {}
MAX_TRIES = 5


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # TODO 1. request.form 에서 username 과 password 를 꺼낸다
        username = request.form.get("username","")
        password = request.form.get("password","")

        # TODO 2. data.USERS 에서 그 아이디를 찾는다
        user = data.USERS.get(username)

        # TODO 3. 없거나 비밀번호가 다르면
        #         flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error") 후
        #         다시 로그인 화면을 보여준다
        if user is None or user["password"] != password:
            flash("아이디 또는 비밀번호가 올바르지 않습니다.","error")
            return render_template("auth/login.html")

        # TODO 4. 맞으면 session["user_id"] 와 session["role"] 에 값을 넣고
        #         url_for("mypage.list_applications") 로 보낸다
        session["user_id"] = user["id"]
        session["role"] = user["role"]
        return redirect(url_for("mypage.list_applications"))

    return render_template("auth/login.html")


@bp.get("/logout")
def logout():
    # TODO. session 을 비우고 메인으로 보낸다
    session.clear()
    return redirect(url_for("main.index"))


@bp.get("/signup")
def signup():
    # 회원가입은 화면만 만듭니다. 기능은 보류입니다.
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

        # 6자리입니다. 4자리면 5회 제한이 있어도 처음부터 다시 요청하며 돌리면 뚫립니다.
        code = f"{secrets.randbelow(1_000_000):06d}"
        RESET_CODES[username] = {"code": code, "tries": 0}

        # 메일은 실제로 보내지 않습니다. 서버를 띄운 사람만 터미널에서 볼 수 있습니다.
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
                # 코드를 버립니다. 다시 요청하면 새 코드가 만들어집니다.
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
    # 1단계(아이디 · 이메일)와 2단계(인증코드)를 모두 통과했는지 확인합니다.
    if username is None or not session.get("reset_verified"):
        flash("본인 확인을 먼저 진행해 주십시오.", "error")
        return redirect(url_for("auth.forgot"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if not password or password != request.form.get("password_confirm", ""):
            flash("비밀번호가 비어 있거나 서로 다릅니다.", "error")
            return render_template("auth/reset.html")

        # 데이터베이스가 없으므로 메모리의 값만 바뀝니다.
        # 서버를 다시 켜면 원래 비밀번호로 돌아갑니다.
        data.USERS[username]["password"] = password
        session.pop("reset_user", None)
        session.pop("reset_verified", None)
        flash("비밀번호를 바꿨습니다. 새 비밀번호로 로그인해 주십시오.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset.html")
