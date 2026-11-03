from flask import Blueprint, render_template

import data

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
    return render_template("main.html", notices=NOTICES, schedule=SCHEDULE)
