"""
Glass House - 원서 접수 시스템

실행 방법
    source venv/bin/activate      (Windows: venv\\Scripts\\Activate.ps1)
    python app.py

이 파일이 하는 일은 두 가지뿐입니다.
  1. Flask 앱을 만든다
  2. routes/ 안의 담당자별 파일을 모아서 등록한다

기능은 routes/ 안에서 만듭니다. 이 파일은 되도록 고치지 마십시오.

  routes/main.py     정욱   메인                  (완성. 참고용 견본)
  routes/auth.py     성원   로그인 · 로그아웃
  routes/mypage.py   성원   내 원서 목록 · 상세
  routes/apply.py    수하   원서 작성 · 합격 조회
  routes/admin.py    종성   심사위원 포털

화면 확인용 주소
    http://localhost:8000/                      메인
    http://localhost:8000/dev/                  만들어진 화면 목록
    http://localhost:8000/dev/login-as/reviewer 관리자로 로그인된 척하기
    http://localhost:8000/dev/logout            로그아웃된 척하기

주의
    HTML 파일을 더블클릭하면 화면이 제대로 나오지 않습니다.
    템플릿 문법은 Flask 가 처리하므로 반드시 이 서버를 띄워서 확인하십시오.
"""
from pathlib import Path

from flask import Flask, redirect, render_template, session, url_for
from jinja2 import TemplateNotFound

import data
from routes import admin, apply, auth, main, mypage

app = Flask(__name__)

# 세션(로그인 상태)을 쿠키에 서명해 저장할 때 쓰는 열쇠입니다.
app.config["SECRET_KEY"] = "dev-only-change-me"

# 담당자별 라우트를 등록합니다.
app.register_blueprint(main.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(mypage.bp)
app.register_blueprint(apply.bp)
app.register_blueprint(admin.bp)

TEMPLATES_DIR = Path(app.root_path) / "templates"


@app.context_processor
def inject_globals():
    """
    모든 템플릿에서 user 와 site 를 바로 쓸 수 있게 넣어 줍니다.
    base.html 의 상단 메뉴가 user 를 보고 모양을 바꿉니다.
    """
    user = data.find_user_by_id(session.get("user_id"))
    return {"user": user, "site": data.SITE}


@app.errorhandler(TemplateNotFound)
def template_not_found(e):
    """
    아직 만들지 않은 화면에 들어갔을 때, 무엇을 만들어야 하는지 알려 줍니다.
    팀원이 작업 순서를 잡는 데 쓰라고 넣어 둔 안내입니다.
    """
    name = e.name
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8"><title>화면 없음</title>
<style>body{{font-family:system-ui,sans-serif;max-width:620px;margin:64px auto;padding:0 16px;line-height:1.75}}
code{{background:#f1f3f5;padding:2px 6px;border-radius:3px}}
pre{{background:#f8f9fa;border:1px solid #dee2e6;padding:14px;border-radius:4px;overflow-x:auto}}
a{{color:#0b63ce}}</style></head>
<body>
<h1>아직 만들지 않은 화면입니다</h1>
<p><code>templates/{name}</code> 파일이 없습니다. 아래 내용으로 만들면 바로 보입니다.</p>
<pre>{{% extends "base.html" %}}

{{% block title %}}화면 이름{{% endblock %}}

{{% block content %}}
&lt;div class="container"&gt;

  &lt;!-- 여기부터 평소처럼 HTML 로 만듭니다 --&gt;

&lt;/div&gt;
{{% endblock %}}</pre>
<p>자세한 내용은 <code>docs/TEAM_GUIDE.md</code> 3절과 맨 아래 명세서를 보십시오.</p>
<p><a href="/dev/">개발용 화면 목록</a> · <a href="/">메인으로</a></p>
</body></html>""", 404


# ---------------------------------------------------------------------------
# 아래는 화면 확인용 임시 라우트입니다.
# 기능이 다 붙으면 통째로 지웁니다.
# ---------------------------------------------------------------------------
@app.get("/dev/")
def dev_index():
    files = sorted(
        str(p.relative_to(TEMPLATES_DIR))
        for p in TEMPLATES_DIR.rglob("*.html")
        if p.name != "base.html" and "components" not in p.parts
    )
    links = "".join(f'<li><a href="/dev/{f}">{f}</a></li>' for f in files)
    accounts = "".join(
        f'<li><a href="/dev/login-as/{u}">{u}</a> ({v["name"]} · {v["role"]})</li>'
        for u, v in data.USERS.items()
    )
    now = data.find_user_by_id(session.get("user_id"))
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8"><title>개발용 화면 목록</title>
<style>body{{font-family:system-ui,sans-serif;max-width:680px;margin:48px auto;padding:0 16px;line-height:1.7}}
h2{{font-size:16px;margin-top:28px}} li{{margin:4px 0}} a{{color:#0b63ce}}
code{{background:#f1f3f5;padding:1px 5px;border-radius:3px}}</style></head>
<body>
<h1>개발용 화면 목록</h1>
<p>현재 로그인: <code>{now["username"] + " / " + now["role"] if now else "비로그인"}</code>
 · <a href="/dev/logout">로그아웃</a> · <a href="/">메인으로</a></p>

<h2>로그인된 척하기</h2>
<ul>{accounts}</ul>

<h2>만들어진 화면</h2>
<ul>{links or "<li>아직 없습니다. templates/ 아래에 파일을 만들면 여기 나타납니다.</li>"}</ul>
</body></html>"""


@app.get("/dev/login-as/<username>")
def dev_login_as(username):
    u = data.USERS.get(username)
    if u:
        session["user_id"] = u["id"]
        session["role"] = u["role"]
    return redirect(url_for("dev_index"))


@app.get("/dev/logout")
def dev_logout():
    session.clear()
    return redirect(url_for("dev_index"))


@app.get("/dev/<path:name>")
def dev_page(name):
    """templates 안의 아무 화면이나 더미 데이터와 함께 열어 봅니다."""
    apps = list(data.APPLICATIONS.values())
    try:
        return render_template(
            name,
            applications=apps,
            application=apps[0],
            notices=main.NOTICES,
            schedule=main.SCHEDULE,
        )
    except TemplateNotFound:
        return (f"<h1>404</h1><p>templates/{name} 파일이 없습니다.</p>"
                f'<p><a href="/dev/">목록으로</a></p>', 404)


if __name__ == "__main__":
    # host="0.0.0.0" 이면 같은 와이파이의 다른 노트북에서도 접속할 수 있습니다.
    app.run(host="0.0.0.0", port=8000, debug=True)
