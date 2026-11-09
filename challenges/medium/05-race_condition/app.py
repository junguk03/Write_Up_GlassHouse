import os

from flask import Flask, session

import data
from config_flags import flag, secret
from routes import admin, apply, auth, main, mypage

app = Flask(__name__)
app.config["SECRET_KEY"] = secret("SECRET_KEY") or os.urandom(16).hex()
app.config["SESSION_COOKIE_NAME"] = "gh_8005"
app.config["FLAG_RACE"] = flag("FLAG_RACE")

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
    # 요청을 스레드로 동시에 처리해야 합니다. 워커를 여러 개 띄우면 data 가 나뉩니다.
    app.run(host="0.0.0.0", port=8005, debug=False, threaded=True)
