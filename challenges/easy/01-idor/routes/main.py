"""
메인 화면  (담당: 정욱)

이 파일은 완성되어 있습니다. 다른 파일을 만들 때 모양을 참고하십시오.

Blueprint 는 라우트를 파일별로 나누기 위한 Flask 기능입니다.
파일마다 Blueprint 를 하나 만들고, app.py 가 그것들을 모아서 등록합니다.
그래서 네 명이 서로 다른 파일을 고쳐도 충돌하지 않습니다.
"""
from flask import Blueprint, render_template

import data

# 첫 번째 인자가 이름입니다. url_for("main.index") 처럼 쓸 때 앞에 붙습니다.
bp = Blueprint("main", __name__)


NOTICES = [
    {"id": 7, "title": "증빙서류 제출 방법 안내", "date": "2026-10-14", "is_new": True},
    {"id": 6, "title": "원서 접수 시스템 점검 안내 (10/18 02:00 ~ 04:00)", "date": "2026-10-12", "is_new": True},
    {"id": 5, "title": "2026학년도 신입생 모집 요강 공고", "date": "2026-10-08", "is_new": False},
    {"id": 4, "title": "입학 설명회 개최 안내", "date": "2026-10-02", "is_new": False},
]

SCHEDULE = [
    {"step": "원서 접수", "period": "2026-10-20 10:00 ~ 11-07 18:00", "state": "예정"},
    {"step": "서류 심사", "period": "2026-11-10 ~ 11-21", "state": "예정"},
    {"step": "1차 합격 발표", "period": "2026-11-25 14:00", "state": "예정"},
    {"step": "면접 전형", "period": "2026-12-01 ~ 12-05", "state": "예정"},
    {"step": "최종 합격 발표", "period": "2026-12-12 14:00", "state": "예정"},
]


@bp.get("/")
def index():
    # render_template(템플릿 파일, 템플릿에 넘길 값들)
    return render_template("main.html", notices=NOTICES, schedule=SCHEDULE)
