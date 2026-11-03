import os

from flask import Flask, session

import data
from config_flags import secret
from routes import admin, apply, auth, files, main, mypage

app = Flask(__name__)
app.config["SECRET_KEY"] = secret("SECRET_KEY") or os.urandom(16).hex()
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

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
