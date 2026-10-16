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
│   ├── .env.example   플래그 변수 이름만 들어 있습니다 (실제 값 없음)
│   ├── schema.sql
│   ├── seed.py
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

```bash
git checkout main
git pull origin main
git checkout -b chal/easy-01-idor

mkdir -p challenges/easy-01-idor
cp -r app challenges/easy-01-idor/challenge
```

Windows에서는 `xcopy /E /I app challenges\easy-01-idor\challenge` 를 사용합니다.

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

플래그 문자열을 코드에 직접 쓰지 않습니다. `.env` 에 두고 `seed.py` 가 읽어서 넣습니다.

**`.env.example`** — 깃에 올립니다. 변수 이름만 알려 주는 견본입니다.

```
FLAG_IDOR=GlassHouse{여기에_실제_플래그}
```

**`.env`** — 깃에 올라가지 않습니다. 실제 플래그를 여기에 적습니다.

```
FLAG_IDOR=GlassHouse{0wn3rsh1p_ch3ck_m1ss1ng}
```

**`seed.py`** — 깃에 올립니다. 데이터베이스에 초기 데이터를 넣는 프로그램입니다.

```python
import os, sqlite3
from dotenv import load_dotenv

load_dotenv()
db = sqlite3.connect("instance/app.db")
db.executescript(open("schema.sql").read())

db.execute("INSERT INTO users (id, username, password, role) VALUES (?,?,?,?)",
           (1,  "applicant01", "test1234", "applicant"))
db.execute("INSERT INTO users (id, username, password, role) VALUES (?,?,?,?)",
           (7,  "victim",      "s3cr3t",   "applicant"))
db.execute("INSERT INTO users (id, username, password, role) VALUES (?,?,?,?)",
           (99, "reviewer",    "adminpw",  "admin"))

# IDOR 목표가 되는 7번 지원자의 원서에 플래그를 심습니다
db.execute(
    "INSERT INTO applications (id, user_id, school, major, intro, status) "
    "VALUES (?,?,?,?,?,?)",
    (42, 7, "하우스고등학교", "정보보호학과",
     f"제 포부는 {os.environ['FLAG_IDOR']} 입니다", "submitted")
)
db.commit()
```

이렇게 나누면 세 가지 이점이 있습니다.

- 깃허브에 올라간 코드를 아무리 읽어도 플래그가 보이지 않습니다.
- 두 조가 **같은 코드로 서로 다른 플래그**를 쓸 수 있습니다.
- 데이터가 꼬이면 `rm instance/app.db && python seed.py` 로 몇 초 만에 초기화됩니다.

플래그는 자동으로 바뀌지 않습니다. `.env` 를 직접 고치고 `seed.py` 를 다시 실행해야 합니다.

### 문제 설명 작성

`challenges/easy-01-idor/README.md` 를 만듭니다.

```markdown
# easy-01 — 접수 내역 조회

|  |  |
|---|---|
| 난이도 | Easy |
| 분류 | Web |
| 출제 | A조 (정욱, 성원) |
| 접속 | http://192.168.0.17:5000 |
| 플래그 형식 | `GlassHouse{...}` |

## 설명

원서 접수 시스템이 열렸습니다. 다른 지원자의 원서는 볼 수 없어야 하는데,
어떤 지원자가 자기소개란에 이상한 문자열을 적어 두었다는 제보가 있습니다.

제공 계정: `applicant01 / test1234`
```

> **취약점 이름을 설명에 쓰지 마십시오.** 제목에도 쓰지 않습니다.
> 폴더 이름에는 들어가지만, 푸는 조에게는 `challenge/` 폴더와 README만 전달합니다.

### 올리기

```bash
git add challenges/easy-01-idor
git status                   # .env 가 보이면 멈춥니다
git commit -m "chal: easy-01 문제 추가"
git push -u origin chal/easy-01-idor
```

`solution/` 폴더는 아직 만들지 않습니다.

---

## 4. 교환하기

화이트박스 방식으로 진행합니다. **소스 코드는 주고, 서버도 띄우고, 플래그만 주지 않습니다.**
공개 대회에서도 같은 방식을 씁니다.

```
출제 조  →  challenge/ 폴더를 브랜치에 올립니다 (.env 없음)
           자기 노트북에서 진짜 플래그로 서버를 띄웁니다
푸는 조  →  코드를 읽으며 취약점을 찾습니다
           익스플로잇을 작성해 출제 조 서버로 보냅니다
           서버 응답에서 진짜 플래그가 나옵니다
```

코드를 읽을 수 있어도 플래그는 서버에만 있으므로, 실제로 공격에 성공해야 얻을 수 있습니다.

### 출제 조

```bash
cd challenges/easy-01-idor/challenge
source venv/bin/activate
cp .env.example .env         # 실제 플래그를 적습니다
python seed.py
python app.py                # host="0.0.0.0" 으로 실행됩니다
```

자기 IP를 확인해 알려 줍니다.

```bash
ipconfig getifaddr en0       # macOS
ipconfig                     # Windows (IPv4 주소 항목)
```

### 푸는 조

```bash
git fetch origin
git checkout chal/easy-01-idor
```

소스는 로컬에서 읽고, 공격은 출제 조의 주소(`http://192.168.0.17:5000`)로 보냅니다.

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

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
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

| 시점 | 위치 | `solution/` 유무 |
|---|---|---|
| 만드는 중 | `chal/...` 브랜치 | 없음 |
| 교환해서 푸는 중 | `chal/...` 브랜치 | 없음 |
| 모두 끝난 뒤 | `main` 의 `challenges/` 폴더 | 있음 |

브랜치는 작업하는 동안만 쓰는 임시 작업대이고, 완성된 문제는 전부 `main` 에 모입니다.
