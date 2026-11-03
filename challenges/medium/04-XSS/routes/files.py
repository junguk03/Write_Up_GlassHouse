import os

from flask import Blueprint, abort, send_from_directory

from paths import UPLOAD_DIR

bp = Blueprint("files", __name__)


@bp.get("/uploads/<name>")
def uploaded(name):
    if not os.path.isfile(os.path.join(UPLOAD_DIR, name)):
        abort(404)
    return send_from_directory(UPLOAD_DIR, name)
