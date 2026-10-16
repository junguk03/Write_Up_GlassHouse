# 팀 개발 가이드

Glass House 프로젝트의 공통 규칙입니다. 작업을 시작하기 전에 끝까지 한 번 읽어 주십시오.

맨 아래 **명세서** 에 적힌 주소, 파일 경로, 입력칸 이름, 변수 이름은 나중에 백엔드 코드가
그대로 가져다 씁니다. 하나라도 다르면 합칠 때 동작하지 않으므로 임의로 바꾸지 말고,
바꿔야 할 사정이 생기면 먼저 말씀해 주십시오.

---

## 1. 이 프로젝트는 어떻게 동작하는가

### 프론트엔드와 백엔드를 폴더로 나누지 않았습니다

보통 웹 개발을 배우면 프론트와 백엔드를 따로 만들고 서버를 두 개 켜는 방식을 먼저 접합니다.
이 프로젝트는 그렇게 하지 않고, Flask 하나 안에 화면과 로직을 같이 둡니다.
이유는 세 가지입니다.

첫째, **이 프로젝트의 목적이 보안 취약점을 재현하는 것**이기 때문입니다.
예를 들어 저장형 XSS는 서버가 HTML을 직접 만들어 내보낼 때 자연스럽게 발생합니다.
프론트를 React 같은 것으로 따로 만들면 그런 취약점을 억지로 심어야 해서 현실성이 떨어집니다.

둘째, **로그인 상태 관리가 단순해집니다.** 서버를 둘로 나누면 주소가 달라서
쿠키가 전달되지 않는 문제를 따로 해결해야 합니다. 그 문제를 푸느라 정작 배우려는
취약점 공부를 못 하게 됩니다.

셋째, **네 명 모두 Flask가 처음**입니다. 배울 것을 절반으로 줄이는 쪽이 맞습니다.

실제 공개된 웹 해킹 문제들은 거의 전부 이 구조를 씁니다.

### 요청 하나가 흐르는 경로

브라우저에서 주소를 입력하면 아래 순서로 처리됩니다.

```
1. 브라우저        GET /login 요청
2. app.py          /login 을 담당하는 함수를 찾아 실행
3. 담당 함수        화면에 뿌릴 데이터를 준비
                   render_template("auth/login.html", 데이터) 호출
4. Jinja(템플릿)    auth/login.html 첫 줄의 extends 를 보고 base.html 을 먼저 읽음
                   base.html 을 위에서 아래로 쓰다가 block content 를 만나면
                   그 자리에 login.html 의 내용을 끼워 넣음
5. Flask           완성된 HTML 한 장을 브라우저로 전송
6. 브라우저        HTML을 읽다가 style.css 를 추가로 요청
7. Flask           static 폴더의 파일을 그대로 전달
```

여기서 기억할 것은 **3번의 `render_template` 한 줄이 화면과 로직이 만나는 지점**이라는 점입니다.
나중에 취약점은 대부분 3번 단계(데이터를 준비하면서 권한 검사를 빠뜨림) 또는
4번 단계(사용자 입력을 그대로 HTML에 넣음)에서 생깁니다.

### 파일별 역할

```
app/
├── app.py                      지금은 화면 확인용 더미 서버입니다.
│                               나중에 주소와 로직을 담당하는 본체가 됩니다.
├── requirements.txt            필요한 라이브러리 목록과 버전입니다.
├── .env.example                설정값 견본입니다. 복사해서 .env 를 만듭니다.
│
├── templates/                  화면(HTML)이 들어가는 곳입니다.
│   ├── base.html               모든 화면의 공통 틀입니다. 헤더·네비·푸터가 여기 있습니다.
│   ├── components/ui.html      버튼·입력칸·카드 같은 공통 부품입니다.
│   ├── main.html               메인(모집 안내) 화면입니다.
│   ├── auth/                   회원가입·로그인
│   ├── mypage/                 내 원서 목록·상세
│   ├── apply/                  원서 작성
│   ├── result/                 합격 조회
│   └── admin/                  심사위원 포털·관리자
│
├── static/                     코드를 거치지 않고 그대로 전달되는 파일입니다.
│   ├── css/style.css           공통 스타일시트입니다.
│   ├── js/                     자바스크립트
│   └── img/                    이미지
│
└── uploads/                    업로드된 파일이 저장될 곳입니다. 깃에 올리지 않습니다.
```

`templates/` 와 `static/` 의 차이를 기억해 주십시오.
`templates/` 안의 파일은 Flask가 한 번 가공해서 내보내고,
`static/` 안의 파일은 가공 없이 그대로 나갑니다.

---

## 2. 시작하기

### 받기

```bash
git clone https://github.com/junguk03/Write_Up_GlassHouse.git
cd Write_Up_GlassHouse/app
```

### 가상환경 만들기 (최초 한 번)

가상환경은 **가상머신이 아닙니다.** UTM이나 VirtualBox처럼 리눅스를 설치하는 것이 아니라,
이 프로젝트에서 쓸 파이썬 라이브러리만 따로 담아 두는 폴더 하나가 생기는 것입니다.
크기는 수십 MB이고 만드는 데 3초 걸리며, 지우고 싶으면 폴더째 삭제하면 됩니다.

```
app/venv/
├── bin/python                      시스템 파이썬을 가리키는 바로가기
└── lib/.../site-packages/flask/    pip install 한 것이 여기 들어갑니다
```

`activate` 명령이 하는 일은 터미널의 PATH 설정 맨 앞에 `venv/bin` 을 끼워 넣는 것뿐입니다.
그래서 `python` 을 치면 시스템 것 대신 이 폴더 안의 것이 먼저 실행됩니다.

venv 폴더는 사람마다 따로 만들며, 깃에 올라가지 않습니다(`.gitignore` 에 등록되어 있습니다).
안에 운영체제별 실행 파일이 들어 있어서 공유해도 다른 컴퓨터에서는 동작하지 않기 때문입니다.

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> PowerShell에서 `이 시스템에서 스크립트를 실행할 수 없으므로` 라는 오류가 나오면
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` 를 먼저 실행한 뒤 다시 시도하십시오.
> 터미널 창 하나에만 적용되므로 안전합니다.

**Windows (명령 프롬프트 cmd)**
```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

`requirements.txt` 로 설치하면 네 명의 라이브러리 버전이 똑같이 맞춰집니다.
`pip install flask` 로 직접 설치하지 마십시오.

### 실행

```bash
python app.py
```

브라우저에서 아래 주소를 엽니다.

| 주소 | 용도 |
|---|---|
| `http://localhost:5000/` | 메인 화면 |
| `http://localhost:5000/dev/` | 지금까지 만들어진 화면 목록 |
| `http://localhost:5000/dev/auth/login.html` | 특정 화면 직접 열기 |
| `http://localhost:5000/dev/toggle-login` | 로그인 상태 전환 (네비가 바뀝니다) |

> **HTML 파일을 더블클릭하면 화면이 제대로 나오지 않습니다.**
> 템플릿 문법은 Flask가 처리하는 것이므로 반드시 서버를 띄워서 확인해야 합니다.

### 매번 작업할 때

터미널을 새로 열면 가상환경이 꺼져 있습니다. 다시 켜야 합니다.

```bash
cd Write_Up_GlassHouse/app
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1
python app.py
```

터미널 줄 앞에 `(venv)` 가 보이면 켜진 것입니다.
이것을 하지 않아 `ModuleNotFoundError: No module named 'flask'` 가 나오는 경우가 가장 많습니다.

---

## 3. 화면 만드는 법

### 결론부터

**공통 영역(헤더·네비·푸터)이 아니면, 자기 html 파일에 가서 평소처럼 HTML 태그로 만들면 됩니다.**
새로 배워야 할 것은 파일을 감싸는 세 줄뿐이고, 그 안쪽은 전부 평소 쓰던 HTML 그대로입니다.

### 파일 만들기

담당 화면의 경로는 아래 명세서 표에 정해져 있습니다. 예를 들어 회원가입 화면이라면
`templates/auth/signup.html` 파일을 새로 만듭니다.

### 기본 뼈대

모든 화면은 아래 모양으로 시작합니다.

```html
{% extends "base.html" %}

{% block title %}회원가입{% endblock %}

{% block content %}

  <!-- 여기부터는 평소 쓰던 HTML 그대로입니다 -->

{% endblock %}
```

세 줄의 뜻은 이렇습니다.

| 줄 | 뜻 |
|---|---|
| `{% extends "base.html" %}` | 공통 틀을 가져다 씁니다. 반드시 첫 줄에 와야 합니다. |
| `{% block title %}` | 브라우저 탭에 표시될 제목입니다. |
| `{% block content %}` | 본문입니다. 여기 안에 자기 화면을 만듭니다. |

`<html>`, `<head>`, `<header>`, 네비, 푸터는 **쓰지 않습니다.**
`base.html` 이 가지고 있으므로, 안 쓴다고 사라지는 것이 아니라 Flask가 알아서 붙여 줍니다.
브라우저가 받는 최종 HTML에는 전부 들어 있습니다.

### 실제 예시

```html
{% extends "base.html" %}
{% from "components/ui.html" import page_header, field, button %}

{% block title %}회원가입{% endblock %}

{% block content %}
<div class="container">

  {{ page_header("회원가입", "원서 접수를 위해 먼저 계정을 만들어 주십시오.") }}

  <form class="form" method="post" action="/signup">

    {{ field("아이디", "username", required=true, help="영문과 숫자 4자 이상") }}
    {{ field("비밀번호", "password", type="password", required=true) }}
    {{ field("비밀번호 확인", "password_confirm", type="password", required=true) }}

    <div class="form-row">
      {{ field("이름", "name", required=true) }}
      {{ field("이메일", "email", type="email", required=true) }}
    </div>

    <div class="form-actions">
      {{ button("취소", "secondary", href="/") }}
      {{ button("가입하기", "primary", type="submit") }}
    </div>

  </form>

</div>
{% endblock %}
```

안쪽을 보면 `<form>`, `<div>` 같은 평범한 HTML입니다.
`{{ field(...) }}` 는 입력칸 한 묶음을 대신 만들어 주는 부품이고,
직접 `<input>` 을 써도 됩니다. 다만 부품을 쓰면 디자인이 저절로 통일됩니다.

### 어디에 무엇을 넣으면 되는가

| 만들려는 것 | 방법 |
|---|---|
| 제목과 설명 | `{{ page_header("제목", "설명") }}` |
| 입력칸 | `{{ field(...) }}` · 긴 글은 `{{ textarea(...) }}` |
| 버튼 | `{{ button("글자", "primary") }}` |
| 목록 한 칸 | `{{ card("제목", "내용") }}` |
| 상태 표시 | `{{ badge("submitted") }}` |
| 표 | `<table class="table">` 를 `<div class="table-wrap">` 로 감쌉니다 |
| 내용이 없을 때 | `{{ empty("등록된 원서가 없습니다.") }}` |

부품의 전체 목록과 인자는 아래 명세서에 있습니다.

### 바깥 여백

본문은 보통 `<div class="container">` 로 감쌉니다. 좌우 여백과 최대 너비가 적용됩니다.
배너처럼 화면 끝까지 꽉 채워야 하는 영역만 바깥에 두고 안쪽에 `container` 를 씁니다.

### 데이터 뿌리기

더미 서버가 넘겨주는 데이터를 화면에 표시할 수 있습니다.
변수 이름은 명세서에 정해져 있으며, 나중에 백엔드가 붙으면 같은 이름으로 진짜 데이터가 들어옵니다.

```html
<!-- 값 하나 출력 -->
<p>{{ application.school }}</p>

<!-- 목록 반복 -->
{% for app in applications %}
  <div class="card">
    <h3 class="card-title">{{ app.school }} / {{ app.major }}</h3>
    {{ badge(app.status) }}
  </div>
{% endfor %}

<!-- 조건 -->
{% if applications %}
  ... 목록 ...
{% else %}
  {{ empty("등록된 원서가 없습니다.") }}
{% endif %}
```

### CSS 규칙

- `static/css/style.css` **한 파일만** 사용합니다.
- 각 화면에 `<style>` 태그를 넣거나 `style="..."` 인라인 스타일을 쓰지 않습니다. 충돌합니다.
- 쓸 수 있는 클래스 이름은 아래 명세서에 정리되어 있습니다.
- 필요한 클래스가 없으면 직접 만들지 말고 담당자(정욱)에게 요청해 주십시오.

### 수정하면 안 되는 파일

아래 세 파일은 전원이 공유하므로 담당자를 통해서만 수정합니다.

```
templates/base.html             공통 틀
templates/components/ui.html    공통 부품
static/css/style.css            공통 스타일
```

고쳐야 할 일이 생기면 직접 고치지 말고 말씀해 주십시오.

---

## 4. 깃 규칙

### 브랜치

`main` 에 직접 올리는 것은 막혀 있습니다. 브랜치를 만들어 작업하고 PR로 올려야 합니다.

| 담당 | 브랜치 이름 |
|---|---|
| 정욱 | `feat/layout-base` |
| 성원 | `feat/auth` |
| 수하 | `feat/apply` |
| 종성 | `feat/admin` |

```bash
git checkout main
git pull origin main          # 작업 전에 항상 최신 상태로 맞춥니다
git checkout -b feat/auth     # 브랜치 생성 (최초 한 번)

# ... 작업 ...

git add .
git status                    # .env 나 instance/ 가 보이면 멈추고 알려 주십시오
git commit -m "feat: 회원가입 · 로그인 화면 추가"
git push -u origin feat/auth
```

올리면 깃허브에 `Compare & pull request` 버튼이 나타납니다.
눌러서 PR을 만들면 정욱이 확인한 뒤 병합합니다. 병합된 브랜치는 삭제합니다.

### 커밋하면 안 되는 것

```
.env           설정값과 플래그
instance/      데이터베이스 파일
uploads/       업로드된 파일
venv/          가상환경
```

`.gitignore` 에 등록되어 있어 자동으로 걸러지지만, 커밋 전에 `git status` 로
한 번 확인하는 습관을 들여 주십시오. 저장소가 공개 상태라 한 번 올라가면
나중에 지워도 기록에 남습니다.

---

## 5. 자주 나오는 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| `ModuleNotFoundError: No module named 'flask'` | 가상환경이 꺼져 있음 | `source venv/bin/activate` |
| 화면이 헤더 없이 나옴 | HTML 파일을 더블클릭함 | `python app.py` 후 localhost로 접속 |
| `TemplateNotFound` | 파일 경로나 이름이 다름 | 명세서의 경로와 대조 |
| `UndefinedError: 'x' is undefined` | 없는 변수를 사용함 | 명세서의 변수 이름 확인 |
| `TemplateSyntaxError` | `{% endblock %}` 등을 빠뜨림 | 여는 태그와 닫는 태그 짝 확인 |
| 한글이 깨짐 | 파일 인코딩 | 에디터에서 UTF-8로 저장 |
| 수정했는데 그대로 | 브라우저 캐시 | 강력 새로고침 (Cmd/Ctrl + Shift + R) |
| 포트 5000이 사용 중 | macOS AirPlay 충돌 | 시스템 설정에서 AirPlay 수신 끄기 |

막히면 30분 이상 혼자 붙잡지 말고 **오류 메시지 전문을 복사해서** 단톡에 올려 주십시오.
스크린샷보다 텍스트가 검색도 되고 빠릅니다.

---
---

# 명세서

여기부터는 서로 맞춰야 하는 약속입니다. **임의로 바꾸지 마십시오.**

## 6-1. 화면 주소 (URL)

네비게이션과 링크가 이 주소를 기준으로 걸려 있습니다.
백엔드가 붙으면 이 주소로 요청이 들어옵니다.

`범위` 칸은 화요일까지 기능까지 만들 것인지, 화면만 만들 것인지를 뜻합니다.

| 주소 | 메서드 | 화면 | 담당 | 범위 |
|---|---|---|---|---|
| `/` | GET | 메인 (모집 안내) | 정욱 | 완료 |
| `/login` | GET, POST | 로그인 | 성원 | 화면 + 기능 |
| `/logout` | GET | 로그아웃 | 성원 | 화면 + 기능 |
| `/mypage` | GET | 내 원서 목록 | 성원 | 화면 + 기능 |
| `/applications/<id>` | GET | 원서 상세 | 성원 | 화면 + 기능 |
| `/apply` | GET, POST | 원서 작성 | 수하 | 화면 + 기능 |
| `/result` | GET | 합격 조회 | 수하 | 화면 + 기능 |
| `/admin` | GET | 지원자 목록 | 종성 | 화면 + 기능 |
| `/admin/applications/<id>` | GET | 원서 상세 (심사) | 종성 | 화면 + 기능 |
| `/admin/applications/<id>/decide` | POST | 합격 · 불합격 처리 | 종성 | 화면 + 기능 |
| `/signup` | GET | 회원가입 | 성원 | **화면만** |
| `/apply/<id>/edit` | GET | 원서 수정 | 수하 | **화면만** |
| `/download` | GET | 첨부파일 다운로드 | 수하 | **화면만** |

**화면만** 으로 표시된 것은 눌러도 아무 일이 일어나지 않아도 괜찮습니다.
일정상 기능을 뒤로 미룬 것이며, 나중에 붙입니다.

`<id>` 자리에는 숫자가 들어갑니다. 예: `/applications/42`

라우트 함수명은 나중에 `url_for('auth.login')` 처럼 링크를 만들 때 사용합니다.
지금은 링크를 `href="/login"` 처럼 주소로 직접 써도 됩니다.

## 6-2. 템플릿 파일 경로

백엔드가 이 경로를 그대로 호출하므로 이름이 바뀌면 코드를 고쳐야 합니다.

```
templates/
├── base.html                  정욱   공통 틀 (수정 금지)
├── components/ui.html         정욱   공통 부품 (수정 금지)
├── main.html                  정욱   메인
├── auth/
│   ├── signup.html            성원   회원가입
│   └── login.html             성원   로그인
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

## 6-3. 폼 입력칸 이름

백엔드는 `request.form["username"]` 으로 값을 꺼냅니다.
HTML에 `name="user_id"` 로 적혀 있으면 동작하지 않으며,
화면은 멀쩡해 보이기 때문에 원인을 찾기 어렵습니다.

| 화면 | `name` 값 | 기능 구현 |
|---|---|---|
| 로그인 | `username` `password` | 화요일에 구현 |
| 원서 작성 | `school` `major` `intro` | 화요일에 구현 |
| 원서 작성 (추가 칸) | `portfolio_url` `document` | **화면만. 기능 보류** |
| 회원가입 | `username` `password` `password_confirm` `name` | **화면만. 기능 보류** |
| 합격 처리 | `decision` (`accepted` 또는 `rejected`) | 화요일에 구현 |

- `intro` 는 자기소개입니다. 길게 쓸 수 있도록 `textarea` 를 사용합니다.
- **기능 보류** 로 표시된 것은 화면만 만들고 동작은 나중에 붙입니다.
  입력칸은 지금 만들어 두되, 눌러도 아무 일이 일어나지 않아도 괜찮습니다.
- `document` 는 증빙서류 파일입니다. 파일 첨부 기능은 일정상 뒤로 미뤘습니다.

**파일 첨부가 있는 `<form>` 에는 `enctype` 이 반드시 필요합니다.**

```html
<form method="post" action="/apply" enctype="multipart/form-data">
  <input type="file" name="document">
</form>
```

이것이 없으면 파일 이름만 전송되고 내용은 넘어가지 않습니다.

## 6-4. 로그인 계정

회원가입 기능은 만들지 않습니다. 아래 계정이 `app.py` 에 미리 들어 있습니다.
데이터베이스는 쓰지 않으며, 서버를 껐다 켜면 처음 상태로 돌아갑니다.

| 아이디 | 비밀번호 | 이름 | 권한 |
|---|---|---|---|
| `applicant01` | `test1234` | 이정욱 | 지원자 |
| `applicant02` | `s3cr3t` | 정민호 | 지원자 |
| `reviewer` | `adminpw` | 심사위원 | 관리자 |

원서는 41번과 42번이 `applicant01` 의 것이고, 43번이 `applicant02` 의 것입니다.
`applicant01` 로 로그인한 상태에서 43번 원서가 보이면 안 됩니다.

## 6-5. 템플릿으로 넘어오는 변수

더미 서버가 지금 넘겨주는 값이며, 백엔드가 붙어도 같은 이름을 씁니다.

### 모든 화면에서 사용 가능

| 변수 | 형태 | 설명 |
|---|---|---|
| `user` | 사전 또는 `None` | 로그인한 사용자. 비로그인이면 `None` |
| `user.id` | 정수 | 사용자 번호 |
| `user.username` | 문자열 | 아이디 |
| `user.name` | 문자열 | 이름 |
| `user.email` | 문자열 | 이메일 |
| `user.role` | 문자열 | `applicant` 또는 `admin` |
| `site` | 사전 | 사이트 공통 정보 |
| `site.name` | 문자열 | 기관명 |
| `site.recruit_title` | 문자열 | 모집 공고 제목 |
| `site.period_start` / `site.period_end` | 문자열 | 접수 시작·마감일 |
| `site.days_left` | 정수 | 마감까지 남은 일수 |
| `site.contact_tel` / `site.contact_email` | 문자열 | 문의처 |
| `site.office_hours` | 문자열 | 운영시간 |

### 화면별

| 변수 | 형태 | 쓰이는 화면 |
|---|---|---|
| `applications` | 목록 | 내 원서 목록, 지원자 목록 |
| `application` | 사전 | 원서 상세, 원서 작성, 심사 상세 |
| `notices` | 목록 | 메인 |
| `schedule` | 목록 | 메인 |

### 원서(`application`) 항목

원서는 아래 **일곱 개 항목만** 가집니다. 꼭 필요한 것만 남겼습니다.

| 키 | 형태 | 설명 |
|---|---|---|
| `id` | 정수 | 원서 번호 |
| `user_id` | 정수 | 이 원서의 주인 |
| `applicant_name` | 문자열 | 지원자 이름 |
| `school` | 문자열 | 출신 학교 |
| `major` | 문자열 | 지원 학과 |
| `intro` | 문자열 | 자기소개 |
| `status` | 문자열 | 아래 표 참고 |

지원 동기, 포트폴리오 주소, 첨부파일 이름, 제출 일시는 당장 필요하지 않아 뺐습니다.
나중에 필요해지면 그때 추가합니다. 화면에 입력칸을 만들어 두는 것은 상관없습니다.

### 상태(`status`) 값

| 값 | 표시 | 뱃지 색 |
|---|---|---|
| `draft` | 작성중 | 회색 |
| `submitted` | 제출완료 | 남색 |
| `reviewing` | 심사중 | 주황 |
| `accepted` | 합격 | 초록 |
| `rejected` | 불합격 | 빨강 |

### 공지(`notices`) · 일정(`schedule`) 항목

| 변수 | 키 |
|---|---|
| `notices` | `id` `title` `date` `is_new` |
| `schedule` | `step` `period` `state` |

## 6-6. 공통 부품 (매크로)

쓰기 전에 파일 위쪽에서 불러와야 합니다.

```html
{% from "components/ui.html" import button, field, card %}
```

| 부품 | 인자 | 설명 |
|---|---|---|
| `button(text, kind, size, href, type, block)` | `kind`: `primary` `secondary` `danger` `ghost` / `size`: `""` `sm` / `href` 를 주면 링크가 됨 / `type`: `button` `submit` / `block=true` 면 가로 전체 | 버튼 |
| `field(label, name, type, value, placeholder, required, help)` | `type`: `text` `password` `email` `tel` `url` `date` `number` | 한 줄 입력칸 |
| `textarea(label, name, value, rows, placeholder, required, help)` | `rows` 기본값 6 | 여러 줄 입력칸 |
| `select(label, name, options, value, required, help)` | `options`: `[("값", "보이는 글자"), ...]` | 선택 목록 |
| `file_field(label, name, accept, required, help)` | `accept`: 예 `".pdf,.png,.jpg"` | 파일 첨부 |
| `card(title, body, meta, href)` | `href` 를 주면 카드 전체가 링크 | 카드 |
| `badge(status)` | `status`: 위 상태 값 | 상태 뱃지 |
| `page_header(title, desc)` | | 화면 제목 |
| `empty(text)` | | 내용 없음 표시 |

사용 예시

```html
{{ button("제출하기", "primary", type="submit") }}
{{ button("목록으로", "secondary", href="/mypage") }}
{{ button("삭제", "danger", size="sm") }}

{{ field("아이디", "username", required=true, help="영문과 숫자 4자 이상") }}
{{ textarea("자기소개", "intro", rows=8, required=true) }}
{{ select("지원 학과", "major", [("sec", "정보보호학과"), ("cs", "컴퓨터공학과")]) }}
{{ file_field("증빙서류", "document", accept=".pdf,.png,.jpg") }}

{{ card("글래스고등학교 / 정보보호학과", "2026-10-14 제출", href="/applications/41") }}
{{ badge("submitted") }}
```

## 6-7. base.html 의 구멍 (블록)

| 블록 이름 | 용도 | 필수 |
|---|---|---|
| `title` | 브라우저 탭 제목 | 권장 |
| `content` | 본문 | 필수 |
| `extra_css` | 이 화면 전용 스타일시트 | 선택 |
| `extra_js` | 이 화면 전용 스크립트 | 선택 |

## 6-8. CSS 클래스 목록

`style.css` 에 정의되어 있습니다. 여기 없는 이름이 필요하면 요청해 주십시오.

### 배치

| 클래스 | 용도 |
|---|---|
| `.container` | 좌우 여백과 최대 너비. 본문을 감쌀 때 사용 |
| `.page-header` `.page-title` `.page-desc` | 화면 제목 영역 |
| `.section` `.section-head` `.section-title` | 구역 구분 |
| `.cols` `.col` | 2단 배치 (좁은 화면에서 자동으로 1단) |
| `.stack` | 자식 요소 사이에 세로 간격 |

### 폼

| 클래스 | 용도 |
|---|---|
| `.form` | `<form>` 전체를 감싸는 흰 상자 |
| `.form-row` | 입력칸 2개를 가로로 배치 |
| `.field` `.field-label` `.required` | 입력칸 묶음 |
| `.input` `.textarea` `.select` `.input-file` | 입력 요소 |
| `.help-text` | 입력칸 아래 설명 (회색) |
| `.field-error` | 입력칸 아래 오류 (빨강) |
| `.form-actions` | 버튼을 오른쪽에 모으는 영역 |

### 버튼

| 클래스 | 용도 |
|---|---|
| `.btn` | 모든 버튼의 기본 |
| `.btn-primary` | 남색. 주요 동작 |
| `.btn-secondary` | 회색 테두리. 보조 동작 |
| `.btn-danger` | 빨강. 삭제·불합격 |
| `.btn-ghost` | 테두리만 |
| `.btn-sm` | 작은 크기 |
| `.btn-block` | 가로 전체 |

### 표 · 목록 · 카드

| 클래스 | 용도 |
|---|---|
| `.table-wrap` `.table` | 표. `table-wrap` 으로 감싸야 좁은 화면에서 가로 스크롤됨 |
| `.card` `.card-link` `.card-head` `.card-title` `.card-meta` `.card-body` | 카드 |
| `.card-grid` | 카드를 격자로 배치 |
| `.notice-list` `.notice` `.notice-title` `.notice-date` `.new` | 공지 목록 |
| `.empty` | 내용이 없을 때 |

### 상태 · 알림

| 클래스 | 용도 |
|---|---|
| `.badge` `.badge-draft` `.badge-submitted` `.badge-reviewing` `.badge-accepted` `.badge-rejected` | 상태 뱃지 |
| `.alert` `.alert-error` `.alert-success` `.alert-info` | 알림 상자 |

### 기타

| 클래스 | 용도 |
|---|---|
| `.muted` | 회색 글자 |
| `.mono` | 고정폭 글꼴 (날짜·번호 등) |
| `.right` | 오른쪽 정렬 |
| `.notes` | 유의사항 목록 |
