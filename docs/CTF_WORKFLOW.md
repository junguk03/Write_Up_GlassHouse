# CTF 문제 제작 · 교환 절차

두 조로 나누어 각자 취약점을 심은 문제를 만들고, 서로 바꾸어 풀어 봅니다.
구조는 공개된 대회 저장소(SekaiCTF)의 방식을 참고했습니다.

---

## 1. 원칙 — 원본은 수정하지 않습니다

```
app/                              서비스 본체입니다. 정상 동작하며 취약점이 없습니다.
                                  여기는 아무도 수정하지 않습니다.

challenges/easy-01-idor/          app/ 을 복사한 사본입니다. A조가 여기서 취약하게 만듭니다.
challenges/easy-02-upload/        또 다른 사본입니다. B조가 여기서 취약하게 만듭니다.
```

두 조가 똑같이 `routes/mypage.py` 를 수정해도 **충돌하지 않습니다.**
경로가 다르면 깃에게는 완전히 다른 파일이기 때문입니다.

```
challenges/easy-01-idor/routes/mypage.py      A조
challenges/easy-02-upload/routes/mypage.py    B조
                         ↑ 경로가 다르므로 충돌이 발생할 수 없습니다
```

사본이 늘어나는 것이 낭비처럼 보이지만 CTF 문제는 이 방식이 표준입니다.
문제마다 독립적으로 실행되고 독립적으로 배포되어야 하며,
한 문제를 고치다가 다른 문제가 깨지는 일이 없어야 하기 때문입니다.

파이썬과 HTML은 파일당 수 KB이므로 문제를 열 개 만들어도 저장소 전체가 1MB를 넘지 않습니다.

---

## 2. 문제 폴더 구조

문제 하나는 아래 세 부분으로 나뉩니다.

```
challenges/easy-01-idor/
├── README.md          문제 설명 · 난이도 · 출제자. 공개해도 되는 내용입니다.
├── challenge/         출제용입니다. 푸는 조에게 전달하는 소스입니다.
│   ├── app.py  routes/  templates/  static/
│   ├── config_flags.py  .env 에서 플래그를 읽어 오는 도우미
│   ├── .env.example     플래그 변수 이름만 들어 있습니다 (실제 값 없음)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
└── solution/          풀이입니다. 상대 조가 다 푼 뒤에 추가합니다.
    ├── solver.py      자동화된 익스플로잇 코드
    └── writeup.md     글로 쓴 풀이
```

`challenge/` 와 `solution/` 을 나누는 것이 핵심입니다.
풀이를 브랜치에 숨길 필요 없이, **폴더를 나중에 추가하기만 하면** 되기 때문에
문제는 처음부터 `main` 에 올려 두어도 답이 새지 않습니다.

폴더 이름은 `<난이도>-<번호>-<취약점>` 으로 통일합니다.
예: `easy-01-idor`, `easy-02-upload`, `medium-01-xss-to-bac`

---

## 3. 문제 만들기

### 폴더 준비

**복사 전에 반드시 `develop` 을 최신화합니다.**
뒤처진 상태에서 복사하면 의도하지 않은 구멍이 섞여 들어갑니다.

```bash
git checkout develop
git pull origin develop
git checkout -b chal/easy-01-idor

mkdir -p challenges/easy-01-idor/challenge
rsync -a --exclude venv --exclude __pycache__ --exclude .env --exclude '*.pyc' \
      app/ challenges/easy-01-idor/challenge/
```

`cp -r` 대신 `rsync` 를 쓰는 이유는 세 가지를 빼고 복사해 주기 때문입니다.

| 제외 | 왜 |
|---|---|
| `venv/` | 사람마다 다시 만드는 폴더입니다. 수십 MB 라 복사하면 무거워집니다 |
| `__pycache__/` | 파이썬이 만든 캐시입니다 |
| **`.env`** | **원본의 플래그가 따라가는 사고를 막습니다** |

Windows 에서 `rsync` 가 없으면 Git Bash 를 쓰거나, 탐색기로 복사한 뒤
`venv`, `__pycache__`, `.env` 를 직접 지웁니다.

복사한 뒤 할 일은 셋입니다.

1. 취약하게 만들기 (검사하는 줄 삭제 또는 변형)
2. 플래그 심기 (`config_flags.py` 추가 후 `data.py` 등에서 사용)
3. `cp .env.example .env` 후 실제 플래그 적기

### 취약하게 만들기

사본에서 검증을 제거하거나 잘못된 검증으로 바꿉니다.
예를 들어 IDOR이라면 소유권 검사를 지웁니다.

```python
# 정상 (app/routes/mypage.py)
row = db.execute("SELECT * FROM applications WHERE id=?", (app_id,)).fetchone()
if row["user_id"] != session["user_id"]:
    abort(403)
return render_template("mypage/detail.html", application=row)

# 취약 (challenges/easy-01-idor/challenge/routes/mypage.py)
row = db.execute("SELECT * FROM applications WHERE id=?", (app_id,)).fetchone()
return render_template("mypage/detail.html", application=row)
```

> 소스를 공개하는 화이트박스 방식이므로 검사를 아예 없애면 금방 발견됩니다.
> Medium 이상에서는 **있어 보이지만 뚫리는 검증**을 넣는 편이 좋습니다.
>
> ```python
> # 로그인할 때만 목록이 채워지고, 원서를 새로 쓰면 갱신되지 않는 허점
> if str(app_id) not in session.get("my_apps", []):
>     abort(403)
> ```

### 플래그 심기

플래그 문자열을 코드에 직접 쓰지 않습니다. `.env` 에 두고 코드가 읽어 씁니다.
데이터베이스를 쓰지 않으므로 별도의 초기화 스크립트는 필요 없습니다.

**`config_flags.py`** — 깃에 올립니다. 플래그를 읽어 오는 도우미입니다.

```python
import os

from dotenv import load_dotenv

load_dotenv()


def flag(name, default="GlassHouse{dummy_flag_not_set}"):
    """.env 가 없어도 앱이 죽지 않도록 더미 값을 돌려줍니다."""
    return os.environ.get(name, default)
```

**`.env.example`** — 깃에 올립니다. 변수 이름만 알려 주는 견본입니다.

```
SECRET_KEY=change-me-per-challenge
FLAG_IDOR=GlassHouse{여기에_실제_플래그를_넣습니다}
```

**`.env`** — 깃에 올라가지 않습니다. 출제 조만 실제 값을 가집니다.

```
SECRET_KEY=a3f9c21b7e
FLAG_IDOR=GlassHouse{0wn3rsh1p_ch3ck_m1ss1ng}
```

### 플래그를 어디에 두는가

**공격에 성공해야만 닿는 자리**에 둡니다. 취약점 종류마다 자리가 다릅니다.

**데이터 안에 — IDOR 용**

```python
# data.py
from config_flags import flag

APPLICATIONS = {
    43: {
        "id": 43, "user_id": 7, "applicant_name": "정민호",
        "school": "미러고등학교", "major": "정보보호학과",
        "intro": f"제 포부는 {flag('FLAG_IDOR')} 입니다.",
        "status": "submitted",
    },
}
```

43번은 남의 원서라 정상 버전에서는 403 으로 막힙니다.
소유권 검사를 지운 취약 버전에서만 보입니다.

**관리자 화면에만 — Broken Access Control 용**

```python
# app.py
app.config["FLAG_ADMIN"] = flag("FLAG_ADMIN")
```

```html
{# templates/admin/list.html #}
<div class="alert alert-info">심사위원 전용 · 내부 코드 {{ config.FLAG_ADMIN }}</div>
```

`config` 는 Jinja 가 기본으로 넘겨주므로 따로 전달하지 않아도 됩니다.

**조건을 달성해야 — 상태 조작 용**

```html
{# templates/result/index.html #}
{% if applications | selectattr("status", "equalto", "accepted") | list %}
  <div class="alert alert-success">합격 인증 코드 {{ config.FLAG_ACCEPTED }}</div>
{% endif %}
```

**파일로 — 경로 조작 용**

`flag.txt` 를 앱 폴더 **바깥**에 두고 `.gitignore` 에 넣습니다.
`/download?file=../../flag.txt` 로 읽어 내야 합니다.

**전용 주소로 — XSS · SSRF 용**

```python
@bp.get("/admin/notice")
def notice():
    require_admin()
    return current_app.config["FLAG_XSS"]
```

지원자 계정으로는 들어갈 수 없습니다.
저장형 XSS 로 심사위원 브라우저에서 호출해야 얻습니다.

### 한 문제에 플래그를 여러 개 두기

`.env` 에 변수를 여러 개 적고 코드에서 골라 쓰면 됩니다.
문제마다 변수 이름을 다르게 두면 같은 코드로 서로 다른 플래그를 쓸 수 있습니다.

```
FLAG_IDOR=GlassHouse{...}
FLAG_ADMIN=GlassHouse{...}
FLAG_ACCEPTED=GlassHouse{...}
```

**플래그를 바꿀 때는 `.env` 만 고치고 서버를 다시 띄우면 됩니다.**
`.env` 는 깃에 올라가지 않으므로 커밋도 PR 도 필요 없습니다.

### 문제 설명 작성

`challenges/easy-01-idor/README.md` 를 만듭니다.

```markdown
# easy-01 — 접수 내역 조회

|  |  |
|---|---|
| 난이도 | Easy |
| 분류 | Web |
| 출제 | A조 (정욱, 성원) |
| 접속 | http://192.168.0.17:8000 |
| 플래그 형식 | `GlassHouse{...}` |

## 설명

원서 접수 시스템이 열렸습니다. 다른 지원자의 원서는 볼 수 없어야 하는데,
어떤 지원자가 자기소개란에 이상한 문자열을 적어 두었다는 제보가 있습니다.

제공 계정: `applicant01 / test1234`
```

> **취약점 이름을 설명에 쓰지 마십시오.** 제목에도 쓰지 않습니다.
> 폴더 이름에는 들어가지만, 푸는 조에게는 `challenge/` 폴더와 README만 전달합니다.

### 올리기

평소 작업과 똑같습니다. 전용 브랜치를 따로 운영할 필요가 없습니다.
`solution/` 을 아직 만들지 않으므로, `develop` 에 병합해도 답이 새지 않습니다.

```bash
git checkout develop
git pull origin develop
git checkout -b chal/easy-01-idor

git add challenges/easy-01-idor
git status                   # .env 가 보이면 멈춥니다
git commit -m "chal: add easy-01 idor challenge"
git push -u origin chal/easy-01-idor
```

PR 을 올려 `develop` 에 병합합니다. 병합한 브랜치는 삭제합니다.

> `solution/` 폴더는 아직 만들지 않습니다. 상대 조가 다 푼 뒤에 따로 추가합니다.

---

## 4. 교환하기

화이트박스 방식으로 진행합니다. **소스 코드는 주고, 서버도 띄우고, 플래그만 주지 않습니다.**
공개 대회에서도 같은 방식을 씁니다.

```
출제 조  →  challenge/ 를 PR 로 올려 develop 에 병합합니다 (.env 는 올라가지 않음)
           자기 노트북에서 진짜 플래그로 서버를 띄웁니다
푸는 조  →  git pull 로 challenge/ 를 받아 코드를 읽습니다
           익스플로잇을 작성해 출제 조 서버로 보냅니다
           서버 응답에서 진짜 플래그가 나옵니다
```

소스를 읽는 것과 공격하는 것은 별개입니다.

| 하는 일 | 대상 |
|---|---|
| 소스 읽기 | 내 노트북의 `challenges/.../challenge/` 파일 |
| 공격하기 | 출제 조 주소 `http://<출제조IP>:8000` |

코드를 읽을 수 있어도 플래그는 출제 조 서버의 `.env` 에만 있으므로,
실제로 공격에 성공해야 얻을 수 있습니다.
로컬에서 띄우면 플래그가 `FLAG_NOT_SET` 으로 나옵니다.


### 출제 조

```bash
cd challenges/easy-01-idor/challenge
source venv/bin/activate
cp .env.example .env         # 실제 플래그를 적습니다
python app.py                # host="0.0.0.0" 으로 실행됩니다

# 또는 도커로
docker compose up --build
```

자기 IP를 확인해 푸는 조에게 알려 줍니다.

```bash
ipconfig getifaddr en0       # macOS
ipconfig                     # Windows (IPv4 주소 항목)
```

> **IP 를 알려 주지 않으면 푸는 조가 접속할 수 없습니다.**
> `localhost` 는 "지금 이 컴퓨터" 라는 뜻이라, 노트북마다 자기 자신을 가리킵니다.
> 푸는 조가 `localhost:8000` 을 열면 **자기 노트북의 서버** 가 뜹니다.
>
> | 누가 | 주소 |
> |---|---|
> | 서버를 띄운 사람 본인 | `http://localhost:8000` |
> | 같은 와이파이의 다른 사람 | `http://192.168.0.17:8000` |
>
> `app.py` 의 `host="0.0.0.0"` 은 "모든 네트워크 통로로 요청을 받겠다" 는 뜻입니다.
> 이것이 없으면 자기 컴퓨터에서만 열립니다.

### 푸는 조

```bash
git checkout develop
git pull origin develop
```

`challenges/easy-01-idor/challenge/` 가 생깁니다. 이 폴더의 파일을 열어 읽습니다.
브랜치를 따로 받을 필요가 없습니다.

공격은 출제 조 주소로 보냅니다.

```bash
curl -c cookie.txt -X POST http://192.168.0.17:8000/login \
     -d "username=applicant01&password=test1234"

curl -b cookie.txt http://192.168.0.17:8000/applications/43
```

브라우저 개발자 도구(F12)의 Application 탭에서 쿠키를 직접 고치거나,
Network 탭에서 주고받은 요청을 확인하는 방법도 많이 씁니다.

### 조건

- 같은 와이파이에 있어야 합니다.
- macOS에서 방화벽 허용 창이 뜨면 허용을 누릅니다.
- 학교 와이파이는 기기 간 통신을 막는 경우가 있습니다. 안 되면 휴대폰 핫스팟을 사용합니다.

### 힌트 공개 순서

막혔을 때 한 단계씩 엽니다.

1. 취약점 분류만 알려 줍니다. (예: "접근 제어 쪽입니다")
2. 취약한 화면을 알려 줍니다. (예: "내 원서 조회")
3. 취약한 파일을 알려 줍니다.

---

## 5. 끝난 뒤 — 풀이 작성과 병합

양쪽이 모두 풀면 `solution/` 폴더를 추가하고 PR을 올려 `main` 에 병합합니다.
병합된 브랜치는 삭제합니다. 최종적으로 모든 문제는 `main` 한 곳에 폴더로 모입니다.

### writeup.md 양식

```markdown
# easy-01 — IDOR

|  |  |
|---|---|
| 난이도 | Easy |
| 취약점 | IDOR / BOLA |
| 출제 | A조 (정욱, 성원) |
| 풀이 | B조 (수하, 종성) |
| 소요 시간 | 40분 |

## 1. 취약점

어느 파일 몇 번째 줄이 문제인지 코드와 함께 적습니다.

## 2. 공격 과정

요청과 응답을 그대로 붙여 넣습니다. 스크린샷이 있으면 같이 넣습니다.

## 3. 원인

"로그인 여부는 확인했지만 이 객체가 이 사람의 것인지는 확인하지 않았다" 와 같이
왜 뚫렸는지 설명합니다.

## 4. 대응 방안

고친 코드를 적습니다. **이 항목의 평가 비중이 가장 큽니다. 빠뜨리지 마십시오.**
```

### solver.py

손으로 푼 공격을 파이썬 스크립트로 한 번 더 자동화해 둡니다.
공부가 되고, 나중에 코드를 고쳤을 때 아직 뚫리는지 바로 확인할 수 있습니다.

```python
import re, sys, requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
s = requests.Session()
s.post(f"{BASE}/login", data={"username": "applicant01", "password": "test1234"})

for app_id in range(1, 100):
    r = s.get(f"{BASE}/applications/{app_id}")
    m = re.search(r"GlassHouse\{[^}]+\}", r.text)
    if m:
        print(f"[+] 원서 {app_id} 번에서 발견: {m.group()}")
        break
```

### README 갱신

병합한 뒤 저장소 루트의 `README.md` 문제 목록 표에 한 줄 추가합니다.

> 두 조가 동시에 `README.md` 를 고치면 그 표에서만 충돌이 납니다.
> 한 조가 먼저 병합하고, 다른 조가 `git pull` 로 받은 뒤 올리면 됩니다.

---

## 6. 요약

| 시점 | 어디에 있나 | `solution/` 유무 |
|---|---|---|
| 만드는 중 | `chal/...` 브랜치 | 없음 |
| 교환해서 푸는 중 | `develop` (병합 완료) | 없음 |
| 모두 끝난 뒤 | `develop` → `main` | 있음 |

`solution/` 을 나중에 추가하는 구조라서, 문제 자체는 만들자마자 `develop` 에 병합해도
답이 새지 않습니다. 푸는 조는 `git pull` 만 하면 됩니다.

브랜치는 작업하는 동안만 쓰는 임시 작업대이고, 완성된 문제는 전부 `main` 에 모입니다.
