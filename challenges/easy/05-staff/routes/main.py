from flask import Blueprint, render_template

import data

bp = Blueprint("main", __name__)


NOTICES = [
    {"id": 7, "title": "확인서류 제출 방법 안내", "date": "2026-10-14", "is_new": True},
    {"id": 6, "title": "초대권 신청 시스템 점검 안내 (10/18 02:00 ~ 04:00)", "date": "2026-10-12", "is_new": True},
    {"id": 5, "title": "2026 크리스마스 파티 개최 공고", "date": "2026-10-08", "is_new": False},
    {"id": 4, "title": "파티 드레스 코드 안내", "date": "2026-10-02", "is_new": False},
]

SCHEDULE = [
    {"step": "초대권 신청", "period": "2026-10-20 10:00 ~ 11-07 18:00", "state": "예정"},
    {"step": "신청서 검토", "period": "2026-11-10 ~ 11-21", "state": "예정"},
    {"step": "1차 당첨 발표", "period": "2026-11-25 14:00", "state": "예정"},
    {"step": "참석 확인", "period": "2026-12-01 ~ 12-05", "state": "예정"},
    {"step": "최종 당첨 발표", "period": "2026-12-12 14:00", "state": "예정"},
]


@bp.get("/")
def index():
    return render_template("main.html", notices=NOTICES, schedule=SCHEDULE)
