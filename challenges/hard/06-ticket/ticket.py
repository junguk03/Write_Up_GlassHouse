import base64
import hashlib
import hmac
import json
import os
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "keys", "ticket_key.json")

COOKIE_NAME = "gh_8010_ticket"
LEGACY_PREFIX = "v1."


def _secret():
    with open(KEY_PATH, encoding="utf-8") as f:
        return json.load(f)["secret"].encode()


def _b64encode(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64decode(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _sign(body):
    return hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()


def _split(token):
    body, _, sig = token.rpartition(".")
    if not body or not hmac.compare_digest(_sign(body), sig):
        return None
    return body


def issue(user_id, username):
    payload = {"tid": user_id, "name": username, "role": "guest"}
    body = _b64encode(json.dumps(payload, separators=(",", ":")).encode())
    return body + "." + _sign(body)


def verify(token):
    if not token or token.startswith(LEGACY_PREFIX):
        return None
    body = _split(token)
    if body is None:
        return None
    try:
        return json.loads(_b64decode(body))
    except ValueError:
        return None


def read_legacy(token):
    body = _split(token[len(LEGACY_PREFIX):])
    if body is None:
        return None
    return pickle.loads(_b64decode(body))
