"""
신청서 작성 · 당첨 조회  (담당: 수하)

쓸 수 있는 데이터는 data.py 의 APPLICATIONS 입니다.
새 신청서를 추가할 때는 data.next_application_id() 로 번호를 받으십시오.

신청서 수정과 첨부파일 다운로드는 화면만 만들고 기능은 보류합니다.

참고
    request.form["school"]        폼에서 보낸 값 꺼내기
    request.files["document"]     첨부파일 꺼내기 (지금은 보류)
    data.APPLICATIONS[번호] = {...}   새 신청서 저장
"""
import base64
import pickle

from flask import (Blueprint, abort, flash, make_response, redirect,
                   render_template, request, session, url_for)

import data

bp = Blueprint("apply", __name__)


@bp.route("/apply", methods=["GET", "POST"])
def create():
    # 1. 로그인하지 않았으면 로그인 화면으로 보낸다
    user = data.find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        # 2. 폼에서 school, major, intro 를 꺼낸다
        school = request.form.get("school", "").strip()
        major = request.form.get("major", "").strip()
        intro = request.form.get("intro", "").strip()

        if not school or not major or not intro:
            flash("소속, 희망 좌석, 신청 사연을 모두 입력해 주십시오.", "error")
            return render_template("apply/form.html", application=None)

        # 3. 새 신청서 번호를 받는다
        app_id = data.next_application_id()

        # 4. 새 신청서를 저장한다 (명세서 6-5 의 일곱 개 항목)
        data.APPLICATIONS[app_id] = {
            "id": app_id,
            "user_id": user["id"],
            "applicant_name": user["name"],
            "school": school,
            "major": major,
            "intro": intro,
            "status": "submitted",
        }

        # 5. 내 신청서 목록으로 보낸다
        flash("신청서가 제출되었습니다.", "success")
        return redirect(url_for("mypage.list_applications"))

    return render_template("apply/form.html", application=None)


@bp.get("/apply/<int:app_id>/edit")
def edit(app_id):
    # 화면만 만듭니다. 기능(저장)은 보류입니다.
    # 로그인하지 않았으면 로그인 화면으로 보낸다
    user = data.find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("auth.login"))

    # 없는 신청서면 404, 내 신청서가 아니면 403
    application = data.APPLICATIONS.get(app_id)
    if application is None:
        abort(404)
    if application["user_id"] != user["id"]:
        abort(403)

    return render_template("apply/form.html", application=application)


@bp.get("/download")
def download():
    # 화면만 만듭니다. 기능은 보류입니다.
    return redirect(url_for("mypage.list_applications"))


@bp.get("/result")
def index():
    # 1. 로그인하지 않았으면 로그인 화면으로 보낸다
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("auth.login"))

    # 2. 내 신청서 중 결과가 나온 것(당첨 · 미당첨)만 모은다
    applications = [
        a for a in data.APPLICATIONS.values()
        if a["user_id"] == user_id and a["status"] in ("accepted", "rejected")
    ]

    # 3. applications 라는 이름으로 템플릿에 넘긴다
    return render_template("result/index.html", applications=applications)


@bp.post("/apply/save")
def save_draft():
    """작성 중인 신청서를 임시저장한다 (pickle -> base64 -> 쿠키)."""
    user = data.find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("auth.login"))
    draft = {
        "school": request.form.get("school", ""),
        "major": request.form.get("major", ""),
        "intro": request.form.get("intro", ""),
    }
    blob = base64.b64encode(pickle.dumps(draft)).decode()
    resp = make_response(redirect(url_for("apply.create")))
    resp.set_cookie("draft", blob)
    flash("임시저장했습니다. '이어쓰기'로 불러올 수 있습니다.", "success")
    return resp


@bp.get("/apply/load")
def load_draft():
    """임시저장한 신청서를 불러온다."""
    user = data.find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("auth.login"))
    blob = request.cookies.get("draft")
    if not blob:
        flash("임시저장된 내용이 없습니다.", "error")
        return redirect(url_for("apply.create"))
    # (!) 사용자 쿠키를 그대로 역직렬화한다  ← 취약점
    draft = pickle.loads(base64.b64decode(blob))
    return render_template("apply/draft.html", draft=draft)