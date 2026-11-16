import os
from urllib.parse import unquote

from flask import Blueprint, abort, send_file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

bp = Blueprint("files", __name__)


@bp.get("/uploads/<path:name>")
def uploaded(name):
    if name.startswith("/") or ".." in name:
        abort(400)
    path = os.path.join(UPLOAD_DIR, unquote(name))
    if not os.path.isfile(path):
        abort(404)
    return send_file(path)
