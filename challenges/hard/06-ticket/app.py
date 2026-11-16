import os

from flask import Flask, session

import data
from config_flags import secret
from routes import admin, apply, auth, files, main, mypage
from routes.files import UPLOAD_DIR

app = Flask(__name__)
app.config["SECRET_KEY"] = secret("SECRET_KEY") or os.urandom(16).hex()
app.config["SESSION_COOKIE_NAME"] = "gh_8010"

app.register_blueprint(main.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(mypage.bp)
app.register_blueprint(apply.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(files.bp)

os.makedirs(UPLOAD_DIR, exist_ok=True)
with open(os.path.join(UPLOAD_DIR, "확인서류_작성_예시.txt"), "w", encoding="utf-8") as f:
    f.write("확인서류 작성 예시\n\n"
            "이름: 홍길동\n"
            "소속: 글래스하우스\n"
            "참석 인원: 1명\n\n"
            "위 사람은 2026 글래스하우스 크리스마스 파티에 참석함을 확인합니다.\n")


@app.context_processor
def inject_globals():
    user = data.find_user_by_id(session.get("user_id"))
    return {"user": user, "site": data.SITE}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8010, debug=False)
