"""
시크릿 산타  (위시리스트 · 프로필 · 엘프 사무실)

쓸 수 있는 데이터는 data.py 의 WISHLISTS 와 USERS 입니다.
"""
from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, session, url_for)
from markupsafe import Markup

import data

bp = Blueprint("santa", __name__)

PROFILE_FIELDS = ("name", "email")


def current_user():
    return data.find_user_by_id(session.get("user_id"))


@bp.get("/wishlist")
def list_wishlists():
    user = current_user()
    if user is None:
        return redirect(url_for("auth.login"))

    wishlists = [w for w in data.WISHLISTS.values() if w["user_id"] == user["id"]]
    return render_template("santa/wishlist_list.html", wishlists=wishlists)


@bp.route("/wishlist/new", methods=["GET", "POST"])
def create_wishlist():
    user = current_user()
    if user is None:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        items = [i.strip() for i in request.form.get("items", "").splitlines() if i.strip()]
        memo = request.form.get("memo", "").strip()

        if not title or not items:
            flash("제목과 선물 목록을 입력해 주십시오.", "error")
            return render_template("santa/wishlist_form.html")

        wishlist_id = data.next_wishlist_id()
        data.WISHLISTS[wishlist_id] = {
            "id": wishlist_id,
            "user_id": user["id"],
            "owner_name": user["name"],
            "title": title,
            "items": items,
            "memo": memo,
        }
        flash("위시리스트를 등록했습니다.", "success")
        return redirect(url_for("santa.list_wishlists"))

    return render_template("santa/wishlist_form.html")


@bp.get("/wishlist/<int:wishlist_id>")
def wishlist_detail(wishlist_id):
    user = current_user()
    if user is None:
        return redirect(url_for("auth.login"))

    wishlist = data.WISHLISTS.get(wishlist_id)
    if wishlist is None:
        abort(404)
    if wishlist["user_id"] != user["id"]:
        abort(403)

    return render_template("santa/wishlist_detail.html", wishlist=wishlist)


@bp.route("/profile", methods=["GET", "POST"])
def profile():
    user = current_user()
    if user is None:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        updates = {k: request.form[k].strip() for k in PROFILE_FIELDS if k in request.form}
        if not all(updates.values()):
            flash("이름과 이메일은 비울 수 없습니다.", "error")
            return render_template("santa/profile.html")

        data.USERS[user["username"]].update(updates)
        session["role"] = data.USERS[user["username"]]["role"]
        flash("프로필을 저장했습니다.", "success")
        return redirect(url_for("santa.profile"))

    return render_template("santa/profile.html")


def require_elf():
    if session.get("role") is None:
        return redirect(url_for("auth.login"))
    if session.get("role") != "admin":
        abort(403)
    return None


@bp.get("/elf")
def elf_office():
    response = require_elf()
    if response is not None:
        return response

    wishlists = list(data.WISHLISTS.values())
    return render_template("santa/elf.html", wishlists=wishlists, preview=None)


@bp.post("/elf/card/preview")
def card_preview():
    response = require_elf()
    if response is not None:
        return response

    to = request.form.get("to", "").strip()
    message = request.form.get("message", "").strip()
    preview = Markup(render_template("santa/card.html", to=to, message=message))

    wishlists = list(data.WISHLISTS.values())
    return render_template("santa/elf.html", wishlists=wishlists, preview=preview,
                           form={"to": to, "message": message})
