# 팀 개발 가이드

Glass House 프로젝트 공통 규칙. **작업 시작 전에 전부 읽어줘.**
여기 적힌 URL·파일 경로·입력칸 이름은 나중에 백엔드 코드가 그대로 갖다 쓴다.
하나라도 다르면 합칠 때 깨지니까 임의로 바꾸지 말고, 바꿔야 하면 말해줘.

---

## 1. 시작하기

### 받기

```bash
git clone https://github.com/junguk03/Write_Up_GlassHouse.git
cd Write_Up_GlassHouse/app
```

### 가상환경 만들기 (최초 1회)

가상환경은 이 프로젝트용 파이썬 라이브러리를 따로 담아두는 폴더야.
다른 과제에 영향을 안 주고, 나중에 버전 맞출 때도 편해서 꼭 써야 해.

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
pip install flask
```

**Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install flask
```

> PowerShell에서 `이 시스템에서 스크립트를 실행할 수 없으므로` 에러가 뜨면
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` 를 먼저 실행하고 다시 해.
> 터미널 창 하나에만 적용되는 거라 안전해.

**Windows (명령 프롬프트 cmd)**
```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install flask
```

### 실행

```bash
python app.py
```

브라우저에서 아래 주소를 연다.

```
http://localhost:5000/dev/auth/login.html      ← 자기 파일 경로를 붙인다
```

> **HTML 파일을 더블클릭하면 안 나온다.** 반드시 서버를 띄워서 봐야 해.
> 템플릿 문법은 Flask가 처리해주는 거라서 브라우저 혼자서는 못 읽어.

### 매번 작업할 때

터미널을 새로 열면 가상환경이 풀려 있어. 다시 켜야 한다.

```bash
cd Write_Up_GlassHouse/app
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1
python app.py
```

터미널 줄 앞에 `(venv)` 가 보이면 켜진 거야. 이거 안 해서
`ModuleNotFoundError: No module named 'flask'` 뜨는 게 제일 흔한 삽질이다.

---

## 2. 템플릿 쓰는 법

### 왜 이렇게 하나

페이지가 12개인데 각자 `<html>` 부터 다 쓰면, 공통 부분(헤더·네비·푸터)이 12번 중복돼.
네비에 메뉴 하나 추가할 때마다 12개 파일을 고쳐야 하고, 셋이 각자 헤더를 만들면
디자인이 셋 다 달라진다.

그래서 **공통 껍데기는 `base.html` 한 장에만 두고, 각자는 자기 화면 안쪽만 쓴다.**

```
안 쓰면:  12개 페이지 × 공통 40줄  = 480줄 중복
쓰면:     base.html 40줄 + 페이지당 1줄 = 52줄
```

Flask만의 특이한 방식이 아니야. Django, Laravel, Rails, Next.js의 layout,
React의 컴포넌트까지 전부 같은 발상이고 이름만 다르다. 한 번 익혀두면 계속 쓴다.

### 쓰는 법

**예전 방식**

```html
<!DOCTYPE html>
<html>
<head> ... </head>
<body>
  <header> ... </header>
  <nav> ... </nav>

  <h1>로그인</h1>
  <form> ... </form>

  <footer> ... </footer>
</body>
</html>
```

**앞으로 쓸 방식** — `templates/auth/login.html`

```html
{% extends "base.html" %}

{% block title %}로그인{% endblock %}

{% block content %}
  <h1>로그인</h1>
  <form method="post" action="/login">
    <input name="username" placeholder="아이디">
    <input name="password" type="password" placeholder="비밀번호">
    <button type="submit">로그인</button>
  </form>
{% endblock %}
```

`<html>`, `<head>`, `<header>`, 네비, 푸터를 **안 쓴다.**

- `{% extends "base.html" %}` — 첫 줄에 쓴다. "공통 틀을 가져다 쓴다"는 뜻.
- `{% block title %}` — 브라우저 탭에 뜰 제목.
- `{% block content %}` — 여기 안에 자기 화면 내용을 넣는다.

Flask가 실행될 때 `base.html` 을 가져와서 `content` 자리에 네 내용을 끼워넣고,
완성된 페이지를 브라우저에 보낸다. 브라우저에는 헤더·푸터가 다 붙어서 보여.

### 공통 부품 쓰기

버튼·카드·입력칸은 직접 만들지 말고 만들어둔 걸 불러 써. 디자인이 통일된다.

```html
{% extends "base.html" %}
{% from "components/ui.html" import card, button, field %}

{% block content %}
  <h1>지원자 목록</h1>

  {{ card("김성원 / 정보보호학과", "심사 대기") }}
  {{ card("박수하 / 컴퓨터공학과", "심사 완료") }}

  {{ button("합격 확정", "danger") }}
{% endblock %}
```

필요한 부품이 없으면 직접 만들지 말고 **정욱한테 말해줘.** 추가해서 올릴게.

### CSS 규칙

- `static/css/style.css` **한 파일만** 쓴다.
- 각 페이지에 `<style>` 태그를 넣거나 `style="..."` 인라인을 쓰지 않는다. 충돌 난다.
- 쓸 수 있는 클래스 이름 목록은 따로 공유한다.
- 꼭 자기 화면 전용 CSS가 필요하면 `static/css/<영역>.css` 로 파일을 만들고
  `{% block extra_css %}` 에 연결한다. 먼저 말해줘.

---

## 3. 약속 — 화면 주소 (URL)

**이게 제일 중요하다.** 내가 네비에 `/login` 을 걸었는데 로그인 페이지가
`/signin` 으로 만들어지면 링크가 죽는다. 이 표대로 간다.

| 주소 | 화면 | 담당 |
|---|---|---|
| `/` | 메인 | 정욱 |
| `/signup` | 회원가입 | 성원 |
| `/login` | 로그인 | 성원 |
| `/logout` | 로그아웃 | 성원 |
| `/mypage` | 내 원서 목록 | 성원 |
| `/applications/<id>` | 원서 상세 | 성원 |
| `/apply` | 원서 작성 | 수하 |
| `/apply/<id>/edit` | 원서 수정 | 수하 |
| `/download` | 첨부파일 다운로드 | 수하 |
| `/result` | 합격 조회 | 수하 |
| `/admin` | 지원자 목록 | 종성 |
| `/admin/applications/<id>` | 원서 상세 (심사) | 종성 |
| `/admin/applications/<id>/decide` | 합격 · 불합격 처리 | 종성 |

`<id>` 자리에는 숫자가 들어간다. 예: `/applications/42`

---

## 4. 약속 — 템플릿 파일 경로

나중에 백엔드 코드가 이 경로를 그대로 부른다. 이름이 바뀌면 코드를 고쳐야 해.

```
templates/
├── base.html                  정욱
├── components/ui.html         정욱
├── main.html                  정욱
├── auth/
│   ├── signup.html            성원
│   └── login.html             성원
├── mypage/
│   ├── list.html              성원   내 원서 목록
│   └── detail.html            성원   원서 상세
├── apply/
│   └── form.html              수하   원서 작성 · 수정 공용
├── result/
│   └── index.html             수하   합격 조회
└── admin/
    ├── list.html              종성   지원자 목록
    └── detail.html            종성   원서 상세 (심사)
```

---

## 5. 약속 — 폼 입력칸 이름

**두 번째로 중요하다.** 백엔드는 `request.form["username"]` 으로 값을 꺼내는데
HTML에 `name="user_id"` 로 적혀 있으면 그냥 에러가 난다.
화면은 멀쩡해 보여서 원인 찾는 데 한참 걸린다.

| 화면 | 입력칸 `name` |
|---|---|
| 회원가입 | `username` `password` `password_confirm` `name` `email` |
| 로그인 | `username` `password` |
| 원서 작성 | `school` `major` `intro` `motivation` `portfolio_url` `document` |

- `intro` = 자기소개, `motivation` = 지원 동기
- `portfolio_url` = 포트폴리오 주소
- `document` = 증빙서류 파일

**파일 업로드 폼에는 `enctype` 이 반드시 들어가야 한다.** (수하 주의)

```html
<form method="post" action="/apply" enctype="multipart/form-data">
  <input type="file" name="document">
</form>
```

이게 없으면 파일 이름만 전송되고 내용은 안 넘어간다.

---

## 6. 깃 규칙

### 브랜치

`main` 에 직접 푸시하면 막힌다. 브랜치를 파고 PR을 올려야 한다.

| 담당 | 브랜치 이름 |
|---|---|
| 정욱 | `feat/layout-base` |
| 성원 | `feat/auth` |
| 수하 | `feat/apply` |
| 종성 | `feat/admin` |

```bash
git checkout main
git pull origin main          # 작업 시작 전에 항상 최신으로
git checkout -b feat/auth     # 브랜치 만들기 (최초 1회)

# ... 작업 ...

git add .
git status                    # .env / instance/ 가 뜨면 멈추고 말해줘
git commit -m "feat: 로그인 · 회원가입 화면 추가"
git push -u origin feat/auth
```

푸시하면 깃허브에 "Compare & pull request" 버튼이 뜬다. 눌러서 PR을 올리면
정욱이 보고 승인 후 병합한다. 병합되면 브랜치는 삭제한다.

### 절대 커밋하면 안 되는 것

```
.env           플래그 원본
instance/      DB 파일
uploads/       업로드된 파일
venv/          가상환경
```

`.gitignore` 에 등록돼 있어서 자동으로 걸러지지만, **커밋 전에 `git status` 로
한 번 확인하는 습관**을 들여줘. 저장소가 public이라 한 번 올라가면
나중에 지워도 기록에 남는다.

### 남의 파일 건드리지 않기

자기 담당 폴더만 수정한다. 공통 파일(`base.html`, `style.css`, `app.py`)을
고쳐야 하면 직접 고치지 말고 정욱한테 말해줘.

---

## 7. 화면 만들면서 같이 해올 것

각 화면에 **어떤 데이터가 필요한지** 목록으로 적어줘.
이게 모이면 그대로 DB 설계가 되고, 백엔드 만들 때 바로 쓴다.
UI 만들면서 자연스럽게 나오는 정보라 따로 시간 안 들어.

예시 — 원서 상세 화면

```
- 학교명
- 학과
- 자기소개 (긴 글)
- 지원 동기 (긴 글)
- 포트폴리오 주소
- 첨부파일 이름
- 제출 상태 (작성중 / 제출완료 / 심사중 / 합격 / 불합격)
- 제출 일시
```

---

## 8. 자주 나는 에러

| 증상 | 원인 | 해결 |
|---|---|---|
| `ModuleNotFoundError: No module named 'flask'` | 가상환경이 꺼져 있음 | `source venv/bin/activate` |
| 화면이 헤더 없이 알몸으로 나옴 | HTML 파일을 더블클릭함 | `python app.py` 띄우고 localhost로 접속 |
| `TemplateNotFound` | 파일 경로나 이름이 다름 | 4번 표와 대조 |
| `jinja2.exceptions.UndefinedError` | 템플릿에서 없는 변수를 씀 | `app.py` 의 더미 데이터 이름 확인 |
| 한글이 깨짐 | 파일 인코딩 | 에디터에서 UTF-8로 저장 |
| 수정했는데 화면이 그대로 | 브라우저 캐시 | 강력 새로고침 (Cmd/Ctrl + Shift + R) |
| PowerShell에서 `activate` 가 안 됨 | 실행 정책 | 1번 항목의 `Set-ExecutionPolicy` 참고 |

---

## 9. 막히면

혼자 30분 넘게 붙잡지 말고 단톡에 **에러 메시지 전체를 복사해서** 올려줘.
스크린샷보다 텍스트가 검색도 되고 빠르다.
