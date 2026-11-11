import os

from flask import Flask, session

import data
from config_flags import flag, secret
from routes import admin, apply, auth, main, mypage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = secret("SECRET_KEY") or os.urandom(16).hex()
app.config["SESSION_COOKIE_NAME"] = "gh_8008"

# 제출 서류 보관함을 준비한다.
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
INTERNAL_DIR = os.path.join(BASE_DIR, "internal")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(INTERNAL_DIR, exist_ok=True)
for _app in data.APPLICATIONS.values():
    with open(os.path.join(UPLOAD_DIR, _app["document"]), "w", encoding="utf-8") as f:
        f.write(f"{_app['applicant_name']} 님이 제출한 증빙서류입니다.\n")
with open(os.path.join(INTERNAL_DIR, "flag.txt"), "w", encoding="utf-8") as f:
    f.write(flag("FLAG_DOWNLOAD"))

app.register_blueprint(main.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(mypage.bp)
app.register_blueprint(apply.bp)
app.register_blueprint(admin.bp)


@app.context_processor
def inject_globals():
    user = data.find_user_by_id(session.get("user_id"))
    return {"user": user, "site": data.SITE}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8008, debug=False)
