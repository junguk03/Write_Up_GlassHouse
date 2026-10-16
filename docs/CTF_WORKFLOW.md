# CTF 문제 제작 · 교환 절차

두 조가 각자 취약점을 심은 문제를 만들고, 서로 바꿔서 푼다.

---

## 1. 원칙 — 원본은 건드리지 않는다

```
app/                              서비스 본체. 정상 동작. 취약점 없음.
                                  여기는 아무도 수정하지 않는다.

challenges/easy-01-idor/          app/ 을 통째로 복사한 사본. A조가 여기서 취약하게 만든다.
challenges/easy-02-upload/        또 다른 사본. B조가 여기서 취약하게 만든다.
```

**충돌 걱정은 안 해도 된다.** 두 조가 똑같이 `routes/mypage.py` 를 고쳐도
경로가 다르면 깃에게는 완전히 다른 파일이다.

```
challenges/easy-01-idor/routes/mypage.py      ← A조
challenges/easy-02-upload/routes/mypage.py    ← B조
                         ↑ 경로가 다르므로 충돌 불가능
```

복사본이 늘어나는 게 낭비처럼 보이지만, CTF 문제는 이게 정석이다.
문제마다 독립적으로 실행되고 독립적으로 배포돼야 하고,
한 문제를 고치다 다른 문제가 깨지는 일이 없어야 하기 때문이다.

파이썬과 HTML은 파일당 몇 KB라 문제 열 개를 복사해도 전체가 1MB를 안 넘는다.

---

## 2. 문제 만들기

### 폴더 만들기

```bash
git checkout main
git pull origin main
git checkout -b chal/easy-01-idor

cp -r app challenges/easy-01-idor      # Windows: xcopy /E /I app challenges\easy-01-idor
```

이름은 `<난이도>-<번호>-<취약점>` 으로 통일한다.
예: `easy-01-idor`, `easy-02-upload`, `medium-01-xss-to-bac`

### 취약하게 만들기

사본에서 검증을 제거한다. 예를 들어 IDOR이면 소유권 검사 한 줄을 지운다.

```python
# 정상 (app/routes/mypage.py)
row = db.execute("SELECT * FROM applications WHERE id=?", (app_id,)).fetchone()
if row["user_id"] != session["user_id"]:
    abort(403)
return render_template("mypage/detail.html", application=row)

# 취약 (challenges/easy-01-idor/routes/mypage.py)
row = db.execute("SELECT * FROM applications WHERE id=?", (app_id,)).fetchone()
return render_template("mypage/detail.html", application=row)
```

### 플래그 심기

플래그 문자열을 코드에 직접 쓰지 않는다. `.env` 에 두고 `seed.py` 가 읽어서 넣는다.

**`.env.example`** — 깃에 올린다. 변수 이름만 알려주는 견본.
```
FLAG_IDOR=GlassHouse{여기에_실제_플래그}
```

**`.env`** — 깃에 안 올라간다. 실제 플래그를 여기 쓴다.
```
FLAG_IDOR=GlassHouse{0wn3rsh1p_ch3ck_m1ss1ng}
```

**`seed.py`** — 깃에 올린다. DB에 초기 데이터를 넣는 프로그램.
```python
import os, sqlite3
from dotenv import load_dotenv

load_dotenv()
db = sqlite3.connect("instance/app.db")
db.executescript(open("schema.sql").read())

db.execute("INSERT INTO users (id, username, password, role) VALUES (?,?,?,?)",
           (1, "applicant01", "test1234", "applicant"))
db.execute("INSERT INTO users (id, username, password, role) VALUES (?,?,?,?)",
           (7, "victim", "s3cr3t", "applicant"))
db.execute("INSERT INTO users (id, username, password, role) VALUES (?,?,?,?)",
           (99, "reviewer", "adminpw", "admin"))

# IDOR 목표가 되는 7번 지원자의 원서에 플래그를 심는다
db.execute(
    "INSERT INTO applications (id, user_id, school, major, intro, status) "
    "VALUES (?,?,?,?,?,?)",
    (42, 7, "하우스대", "정보보호", f"제 포부는 {os.environ['FLAG_IDOR']} 입니다", "submitted")
)
db.commit()
```

플래그를 바꾸려면 `.env` 한 줄만 고치고 `python seed.py` 를 다시 돌린다.
데이터가 꼬이면 `rm instance/app.db && python seed.py` 로 몇 초 만에 초기화된다.

### 올리기

```bash
git add challenges/easy-01-idor
git status                   # .env 가 뜨면 멈춘다
git commit -m "chal: easy-01 IDOR 문제 추가"
git push -u origin chal/easy-01-idor
```

> **이 시점에 `WRITEUP.md` 는 올리지 않는다.** 답이 노출된다.
> 상대 조가 다 푼 뒤에 작성해서 같이 병합한다.

---

## 3. 교환하기

### 기본 방식 — 네트워크로 접속한다

문제를 만든 조가 자기 노트북에서 서버를 띄우고, 상대 조는 브라우저로 접속해서 푼다.
**코드를 주고받지 않는다.** 실제 CTF와 같은 조건이라 더 재밌고, 플래그 전달 문제도 없다.

**출제 조**
```bash
cd challenges/easy-01-idor
source venv/bin/activate
python seed.py
python app.py --host=0.0.0.0        # 또는 app.run(host="0.0.0.0", port=5000)
```

자기 IP를 확인해서 알려준다.
```bash
ipconfig getifaddr en0       # macOS
ipconfig                     # Windows — IPv4 주소 항목
```

**푸는 조** — 브라우저에서 `http://<출제조_IP>:5000` 으로 접속한다.

### 조건

- 같은 와이파이에 있어야 한다.
- macOS에서 방화벽 허용 팝업이 뜨면 허용을 누른다.
- 학교 와이파이는 기기 간 통신을 막는 경우가 있다. 안 되면 휴대폰 핫스팟을 쓴다.

### 그래도 안 되면

출제 조가 `.env` 파일 내용을 단톡 DM으로 보내고, 푸는 조가 브랜치를 받아서
자기 노트북에서 띄운다.

```bash
git fetch origin
git checkout chal/easy-01-idor
cd challenges/easy-01-idor
# 받은 내용으로 .env 를 직접 만든다
python seed.py && python app.py
```

이 방식은 소스코드가 다 보이니까 난이도가 확 내려간다. 최후의 수단으로만 쓴다.

### 힌트 주는 순서

막혔을 때 한 단계씩 연다.

1. 취약점 종류만 알려준다 (예: "접근 제어 쪽이야")
2. 취약한 화면을 알려준다 (예: "내 원서 조회")
3. 소스코드를 연다 (화이트박스 전환)

---

## 4. 끝난 뒤 — 라이트업 쓰고 병합

양쪽이 다 풀면 `WRITEUP.md` 를 쓰고 PR을 올려 `main` 에 병합한다.
병합되면 브랜치는 삭제한다. **최종적으로 모든 문제는 `main` 한 곳에 폴더로 모인다.**

`challenges/easy-01-idor/WRITEUP.md` 형식을 통일한다.

```markdown
# easy-01 — IDOR

| | |
|---|---|
| 난이도 | Easy |
| 취약점 | IDOR / BOLA |
| 출제 | A조 (정욱, 성원) |
| 플래그 | `GlassHouse{...}` |

## 취약점

어느 파일 몇 번째 줄이 문제인지, 코드 조각과 함께.

## 공격 과정

요청과 응답을 그대로. 스크린샷이 있으면 같이.

## 왜 뚫렸나

로그인은 확인했지만 "이 객체가 이 사람 것인가"를 확인하지 않았다 — 같은 설명.

## 대응 방안

고친 코드. **이 항목이 평가 비중이 제일 크다. 빠뜨리지 않는다.**
```

병합 후 루트 `README.md` 의 문제 목록 표에 한 줄 추가한다.

> 두 조가 동시에 `README.md` 를 고치면 그 표에서만 충돌이 난다.
> 사소하니까 한 조가 먼저 병합하고, 다른 조가 `git pull` 받은 뒤 올리면 된다.

---

## 5. 요약

| 시점 | 어디에 있나 |
|---|---|
| 만드는 중 | `chal/...` 브랜치 |
| 교환해서 푸는 중 | `chal/...` 브랜치 (답 노출 방지) |
| 다 끝난 뒤 | `main` 의 `challenges/` 폴더 |

브랜치는 작업하는 동안만 쓰는 임시 작업대고, 완성품은 전부 `main` 에 모인다.
