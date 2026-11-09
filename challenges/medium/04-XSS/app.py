import os

from flask import Flask, session

import data
from config_flags import flag, secret
from paths import INTERNAL_DIR
from routes import admin, apply, auth, files, main, mypage

app = Flask(__name__)
app.config["SECRET_KEY"] = secret("SECRET_KEY") or os.urandom(16).hex()
app.config["SESSION_COOKIE_NAME"] = "gh_8005"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

WAITLIST = """2026학년도 신입생 수시 추가 합격자 명단 (대외비)

발표일 전까지 외부 공개를 금지합니다.
명단 열람 확인 코드: {flag}
"""

os.makedirs(INTERNAL_DIR, exist_ok=True)
with open(os.path.join(INTERNAL_DIR, "waitlist.txt"), "w", encoding="utf-8") as f:
    f.write(WAITLIST.format(flag=flag("FLAG_XSS")))

app.register_blueprint(main.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(mypage.bp)
app.register_blueprint(apply.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(files.bp)


@app.context_processor
def inject_globals():
    user = data.find_user_by_id(session.get("user_id"))
    return {"user": user, "site": data.SITE}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8005, debug=False, threaded=True)
