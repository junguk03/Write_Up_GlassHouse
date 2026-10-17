"""
Glass House - UI 확인용 더미 서버

지금은 화면만 확인하기 위한 임시 서버입니다.
로그인도 DB도 없고, 아래 FAKE 데이터를 템플릿에 그대로 넘겨줍니다.

실행 방법
    source venv/bin/activate      (Windows: venv\\Scripts\\Activate.ps1)
    python app.py

확인 주소
    http://localhost:5000/                      메인 페이지
    http://localhost:5000/dev/                  만들어진 화면 전체 목록
    http://localhost:5000/dev/auth/login.html   특정 화면 직접 열기
    http://localhost:5000/dev/toggle-login      로그인 상태 전환 (네비가 바뀝니다)

주의
    HTML 파일을 더블클릭하면 화면이 제대로 나오지 않습니다.
    템플릿 문법은 Flask 가 처리하므로 반드시 이 서버를 띄워서 확인하십시오.
"""

from pathlib import Path

from flask import Flask, redirect, render_template, url_for
from jinja2 import TemplateNotFound

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-only"

TEMPLATES_DIR = Path(app.root_path) / "templates"


# ---------------------------------------------------------------------------
# 사이트 공통 정보
# ---------------------------------------------------------------------------
SITE = {
    "name": "글래스하우스 정보보호학과",
    "recruit_title": "2026학년도 신입생 수시 원서 접수",
    "period_start": "2026-10-20",
    "period_end": "2026-11-07",
    "days_left": 22,
    "contact_tel": "02-123-4567",
    "contact_email": "admission@glasshouse.ac.kr",
    "office_hours": "평일 09:00 - 18:00 (점심시간 12:00 - 13:00)",
}


# ---------------------------------------------------------------------------
# 데이터
#
# 데이터베이스는 쓰지 않습니다. 아래 파이썬 변수가 저장소 역할을 합니다.
# 서버를 껐다 켜면 처음 상태로 돌아가며, 그 편이 실습에는 오히려 편합니다.
#
# 원서 항목은 최소한으로 줄였습니다.
# 지원동기, 포트폴리오 주소, 첨부파일은 나중에 필요해질 때 추가합니다.
#
# 키 이름은 docs/TEAM_GUIDE.md 의 명세서와 반드시 일치시켜야 합니다.
# ---------------------------------------------------------------------------

# 로그인 계정 (회원가입 없이 미리 정해 둔 계정만 사용합니다)
USERS = {
    "applicant01": {"id": 1,  "password": "test1234", "name": "이정욱", "role": "applicant"},
    "applicant02": {"id": 7,  "password": "s3cr3t",   "name": "정민호", "role": "applicant"},
    "reviewer":    {"id": 99, "password": "adminpw",  "name": "심사위원", "role": "admin"},
}

# 원서
#   id              원서 번호
#   user_id         이 원서의 주인.  IDOR 문제의 핵심이 되는 항목입니다.
#   applicant_name  지원자 이름
#   school / major  출신 학교 · 지원 학과
#   intro           자기소개.  나중에 플래그를 숨기거나 XSS를 터뜨릴 자리입니다.
#   status          draft / submitted / reviewing / accepted / rejected
APPLICATIONS = {
    41: {
        "id": 41, "user_id": 1, "applicant_name": "이정욱",
        "school": "글래스고등학교", "major": "정보보호학과",
        "intro": "보안에 관심이 많아 3년간 동아리에서 활동했습니다.",
        "status": "submitted",
    },
    42: {
        "id": 42, "user_id": 1, "applicant_name": "이정욱",
        "school": "하우스고등학교", "major": "컴퓨터공학과",
        "intro": "웹 서비스를 직접 만들어 본 경험이 있습니다.",
        "status": "draft",
    },
    43: {
        "id": 43, "user_id": 7, "applicant_name": "정민호",
        "school": "미러고등학교", "major": "정보보호학과",
        "intro": "남의 원서입니다. 1번 사용자에게는 보이면 안 됩니다.",
        "status": "submitted",
    },
}

# 더미 서버가 템플릿에 넘겨 줄 값
FAKE_USER = dict(USERS["applicant01"], username="applicant01")
FAKE_APPLICATIONS = [APPLICATIONS[41], APPLICATIONS[42]]

FAKE_NOTICES = [
    {"id": 7, "title": "증빙서류 제출 방법 안내", "date": "2026-10-14", "is_new": True},
    {"id": 6, "title": "원서 접수 시스템 점검 안내 (10/18 02:00 ~ 04:00)", "date": "2026-10-12", "is_new": True},
    {"id": 5, "title": "2026학년도 신입생 모집 요강 공고", "date": "2026-10-08", "is_new": False},
    {"id": 4, "title": "입학 설명회 개최 안내", "date": "2026-10-02", "is_new": False},
]

FAKE_SCHEDULE = [
    {"step": "원서 접수", "period": "2026-10-20 10:00 ~ 11-07 18:00", "state": "예정"},
    {"step": "서류 심사", "period": "2026-11-10 ~ 11-21", "state": "예정"},
    {"step": "1차 합격 발표", "period": "2026-11-25 14:00", "state": "예정"},
    {"step": "면접 전형", "period": "2026-12-01 ~ 12-05", "state": "예정"},
    {"step": "최종 합격 발표", "period": "2026-12-12 14:00", "state": "예정"},
]

# 로그인 상태를 켜고 끄기 위한 임시 스위치입니다.
# /dev/toggle-login 으로 바꿀 수 있습니다.
STATE = {"logged_in": False}


@app.context_processor
def inject_globals():
    """모든 템플릿에서 user 와 site 를 바로 쓸 수 있게 넣어 줍니다."""
    return {
        "user": FAKE_USER if STATE["logged_in"] else None,
        "site": SITE,
    }


# ---------------------------------------------------------------------------
# 화면
# ---------------------------------------------------------------------------
@app.get("/")
def index():
    return render_template(
        "main.html",
        notices=FAKE_NOTICES,
        schedule=FAKE_SCHEDULE,
    )


@app.get("/dev/")
def dev_index():
    """templates 폴더에 있는 html 파일을 전부 모아 목록으로 보여 줍니다."""
    files = sorted(
        str(p.relative_to(TEMPLATES_DIR))
        for p in TEMPLATES_DIR.rglob("*.html")
        if p.name != "base.html" and "components" not in p.parts
    )
    links = "".join(
        f'<li><a href="/dev/{f}">{f}</a></li>' for f in files
    )
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8"><title>화면 목록</title>
<style>body{{font-family:system-ui,sans-serif;max-width:640px;margin:48px auto;padding:0 16px}}
li{{margin:6px 0}} a{{color:#0b63ce}}</style></head>
<body>
<h1>만들어진 화면 목록</h1>
<p><a href="/">메인 페이지</a> · <a href="/dev/toggle-login">로그인 상태 전환</a>
(현재: {"로그인" if STATE["logged_in"] else "비로그인"})</p>
<ul>{links}</ul>
</body></html>"""


@app.get("/dev/toggle-login")
def dev_toggle_login():
    STATE["logged_in"] = not STATE["logged_in"]
    return redirect(url_for("dev_index"))


@app.get("/dev/<path:name>")
def dev_page(name):
    """templates 안의 아무 화면이나 더미 데이터와 함께 열어 봅니다."""
    try:
        return render_template(
            name,
            applications=FAKE_APPLICATIONS,
            application=FAKE_APPLICATIONS[0],
            notices=FAKE_NOTICES,
            schedule=FAKE_SCHEDULE,
        )
    except TemplateNotFound:
        return (
            f"<h1>404</h1><p>templates/{name} 파일이 없습니다.</p>"
            f'<p><a href="/dev/">목록으로</a></p>',
            404,
        )


if __name__ == "__main__":
    # host="0.0.0.0" 으로 두면 같은 와이파이의 다른 노트북에서도 접속할 수 있습니다.
    app.run(host="0.0.0.0", port=5000, debug=True)
