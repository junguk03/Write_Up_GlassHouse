"""
문서 변환 도구 (내부 전용)

원서 사이트가 올라온 확인서류의 '미리보기'를 만들 때 이 도구를 부릅니다.
바깥에는 공개하지 않습니다. 같은 서버 안(내부망)에서만 web 이 호출합니다.
"""
import os

import yaml
from flask import Flask, request

app = Flask(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
FLAG_PATH = "/srv/flag.txt"


def _drop_flag():
    """서버가 켜질 때 플래그를 내부 파일로 떨궈 둡니다. 웹으로는 보이지 않습니다."""
    flag = os.environ.get("FLAG_E07_CONVERT", "GlassHouse{dummy_flag_not_set}")
    try:
        with open(FLAG_PATH, "w", encoding="utf-8") as f:
            f.write(flag)
    except OSError:
        pass


@app.get("/convert")
def convert():
    name = request.args.get("name", "")
    if name.startswith("/") or ".." in name:
        return "bad name", 400

    path = os.path.join(UPLOAD_DIR, name)
    if not os.path.isfile(path):
        return "not found", 404

    with open(path, "rb") as f:
        raw = f.read()
        
    data = yaml.load(raw, Loader=yaml.Loader)

    return {"preview": str(data)[:200]}


if __name__ == "__main__":
    _drop_flag()
    # 내부망 전용. docker-compose 에서 바깥 포트를 열지 않습니다.
    app.run(host="0.0.0.0", port=9000)
