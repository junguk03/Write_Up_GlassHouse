import os
import queue
import threading

from flask import Flask, jsonify, request
from playwright.sync_api import sync_playwright

app = Flask(__name__)

TARGET_URL = os.environ.get("TARGET_URL", "http://web:8009")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
VIEW_SECONDS = int(os.environ.get("VIEW_SECONDS", "5"))
QUEUE_SIZE = 10

jobs = queue.Queue(maxsize=QUEUE_SIZE)


def review(app_id):
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        try:
            page = browser.new_context().new_page()
            page.set_default_timeout(10000)

            page.goto(f"{TARGET_URL}/login")
            page.fill("#f-username", "reviewer")
            page.fill("#f-password", ADMIN_PASSWORD)
            page.click("button[type=submit]")
            page.wait_for_load_state("load")

            page.goto(f"{TARGET_URL}/admin/applications/{app_id}")
            link = page.query_selector("a.attachment")
            if link is not None:
                page.goto(TARGET_URL + link.get_attribute("href"))
                page.wait_for_timeout(VIEW_SECONDS * 1000)
        finally:
            browser.close()


def worker():
    while True:
        app_id = jobs.get()
        try:
            review(app_id)
            print(f"[bot] reviewed application {app_id}", flush=True)
        except Exception as exc:
            print(f"[bot] application {app_id} failed: {type(exc).__name__}: {exc}", flush=True)
        finally:
            jobs.task_done()


@app.post("/visit")
def visit():
    payload = request.get_json(silent=True) or {}
    app_id = payload.get("app_id")

    if not isinstance(app_id, int) or isinstance(app_id, bool) or app_id <= 0:
        return jsonify({"ok": False, "error": "app_id must be a positive integer"}), 400

    try:
        jobs.put_nowait(app_id)
    except queue.Full:
        return jsonify({"ok": False, "error": "busy"}), 429

    return jsonify({"ok": True}), 202


threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
