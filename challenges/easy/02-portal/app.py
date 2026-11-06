import os

from flask import Flask, session

import data
from config_flags import flag, secret
from routes import admin, apply, auth, main, mypage

app = Flask(__name__)
app.config["SECRET_KEY"] = secret("SECRET_KEY") or os.urandom(16).hex()
app.config["SESSION_COOKIE_NAME"] = "gh_8002"
app.config["FLAG_ADMIN"] = flag("FLAG_ADMIN")

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
    app.run(host="0.0.0.0", port=8002, debug=False)
