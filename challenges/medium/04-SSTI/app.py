import os

from flask import Flask, session
from jinja2 import TemplateNotFound

import data
from config_flags import secret
from routes import admin, apply, auth, main, mypage

app = Flask(__name__)

app.config["SECRET_KEY"] = secret("SECRET_KEY") or os.urandom(16).hex()

app.config["SESSION_COOKIE_NAME"] = "gh_8006"

app.register_blueprint(main.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(mypage.bp)
app.register_blueprint(apply.bp)
app.register_blueprint(admin.bp)

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
<p><a href="/">메인으로</a></p>
</body></html>""", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8006, debug=False)
