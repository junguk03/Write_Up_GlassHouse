# easy-01 — 접수 내역 조회

|  |  |
|---|---|
| 난이도 | Easy |
| 분류 | Web |
| 출제 | (조 이름) |
| 접속 | `http://<출제조IP>:8000` |
| 플래그 형식 | `GlassHouse{...}` |

## 설명

글래스하우스 정보보호학과 원서 접수가 시작되었습니다.
지원자는 자기가 제출한 원서만 볼 수 있어야 합니다.

그런데 한 지원자가 자기소개란에 이상한 문자열을 적어 두었다는 제보가 있습니다.
그 원서를 찾아 주십시오.

**제공 계정** `applicant01` / `test1234`

## 푸는 쪽 준비

```bash
cd challenges/easy-01-idor/challenge
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

로컬에서 띄우면 플래그가 `FLAG_NOT_SET` 으로 나옵니다.
**실제 플래그는 출제 조 서버에만 있습니다.** 소스는 로컬에서 읽고,
공격은 출제 조 주소로 보내십시오.

## 출제 쪽 준비

```bash
cd challenges/easy-01-idor/challenge
cp .env.example .env            # 실제 플래그를 적습니다
docker compose up --build       # 또는 python app.py
```

자기 IP를 확인해 푸는 조에게 알려 줍니다.

```bash
ipconfig getifaddr en0          # macOS
ipconfig                        # Windows
```

## 힌트

막혔을 때 한 단계씩 엽니다.

<details>
<summary>힌트 1</summary>

접근 제어 쪽입니다. 로그인은 제대로 동작합니다.
</details>

<details>
<summary>힌트 2</summary>

내 원서 목록에는 내 것만 나옵니다. 목록을 거치지 않고 가는 길은 없을까요?
</details>

<details>
<summary>힌트 3</summary>

`routes/mypage.py` 의 `detail()` 과 `routes/apply.py` 의 `edit()` 을 비교해 보십시오.
</details>
