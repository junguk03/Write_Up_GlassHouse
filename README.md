# Write_Up_GlassHouse

원서 접수/관리 시스템을 대상으로 한 웹 취약점 진단 및 모의해킹 프로젝트.
실제 서비스에서 발생할 수 있는 취약점을 재현하고, 공격과 대응 방안을 문서화한다.

## 문서

| 문서 | 내용 |
|---|---|
| [팀 개발 가이드](docs/TEAM_GUIDE.md) | **작업 시작 전 필독.** 환경 설정, 템플릿 사용법, URL·파일명·입력칸 약속, 깃 규칙 |
| [CTF 문제 제작 · 교환 절차](docs/CTF_WORKFLOW.md) | 문제 만드는 법, 플래그 관리, 두 조 교환 방식, 라이트업 양식 |

## 구조

```
.
├── app/           서비스 본체 (취약점 없는 정상 버전). 여기는 수정하지 않는다
├── challenges/    CTF 문제 모음 (app/ 복사 + 취약점 주입)
└── docs/          설계 문서 · 팀 가이드
```

## 실행

```bash
cd app
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py                 # http://localhost:5000
```

현재는 화면 확인용 더미 서버입니다. 데이터베이스와 로그인은 아직 붙지 않았습니다.
`http://localhost:5000/dev/` 에서 지금까지 만들어진 화면 목록을 볼 수 있습니다.

자세한 설명과 운영체제별 차이는 [팀 개발 가이드](docs/TEAM_GUIDE.md)를 본다.

## 문제 목록

| 난이도 | 문제 | 취약점 | 출제 | 라이트업 |
|---|---|---|---|---|
| | *(화요일 회의 후 채움)* | | | |

## 팀

| 담당 | 이름 | 영역 | 브랜치 |
|---|---|---|---|
| 1 | 정욱 | 공통 레이아웃 · 컴포넌트 · 메인 | `feat/layout-base` |
| 2 | 성원 | 회원가입 · 로그인 · 마이페이지 | `feat/auth` |
| 3 | 수하 | 원서 작성 · 증빙서류 첨부 · 합격자 조회 | `feat/apply` |
| 4 | 종성 | 심사위원 포털 · 합격 확정 · 관리자 | `feat/admin` |

## 규칙

- 브랜치 구성: `main`(안정판) ← `develop`(작업 통합) ← `feat/...`(개인 작업).
- `main` 과 `develop` 직접 푸시 금지. `feat/...` → Pull Request → 승인 → `develop` 병합.
- `.env`, `instance/`, `uploads/`, `venv/` 는 커밋하지 않는다. 플래그가 공개된다.
- 커밋 전에 `git status` 로 위 항목이 안 뜨는지 확인한다.
- 공통 파일(`base.html`, `style.css`, `app.py`)은 담당자를 통해 수정한다.
