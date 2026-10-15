# Write_Up_GlassHouse

원서 접수/관리 시스템을 대상으로 한 웹 취약점 진단 및 모의해킹 프로젝트.
실제 서비스에서 발생할 수 있는 취약점을 재현하고, 공격과 대응 방안을 문서화한다.

## 구조

```
.
├── app/           서비스 본체 (취약점 없는 정상 버전)
├── challenges/    CTF 문제 모음 (app/ 복사 + 취약점 주입)
└── docs/          설계 문서
```

## 실행

```bash
cd app
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python seed.py                # DB 생성 + 초기 데이터
python app.py                 # http://localhost:5000
```

## 문제 목록

| 난이도 | 문제 | 취약점 | 라이트업 |
|---|---|---|---|
| | *(화요일 회의 후 채움)* | | |

## 팀

| 담당 | 이름 | 영역 |
|---|---|---|
| 1 | 정욱 | 공통 레이아웃 · 컴포넌트 · 메인 |
| 2 | 성원 | 회원가입 · 로그인 · 마이페이지 |
| 3 | 수하 | 원서 작성 · 증빙서류 첨부 · 합격자 조회 |
| 4 | 종성 | 심사위원 포털 · 합격 확정 · 관리자 |

## 규칙

- `main` 직접 푸시 금지. 브랜치 → Pull Request → 병합.
- `.env`, `instance/`, `uploads/` 는 커밋하지 않는다. 플래그가 공개된다.
