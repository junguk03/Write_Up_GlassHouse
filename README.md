# Write_Up_GlassHouse

초대권 신청/관리 시스템을 대상으로 한 웹 취약점 진단 및 모의해킹 프로젝트.
실제 서비스에서 발생할 수 있는 취약점을 재현하고, 공격과 대응 방안을 문서화한다.

## 문서

| 문서 | 내용 |
|---|---|
| [팀 개발 가이드](docs/TEAM_GUIDE.md) | 작업 시작 전 필독. 환경 설정, 템플릿 사용법, URL·파일명·입력칸 약속, 깃 규칙 |
| [CTF 규칙](docs/RULES.md) | 출제 규칙 · 풀이 규칙 (diff 금지, AI 사용 범위 등) |
| [CTF 문제 제작 · 교환 절차](docs/CTF_WORKFLOW.md) | 문제 만드는 법, 플래그 관리, 두 조 교환 방식, 라이트업 양식 |

## 구조

```
.
├── app/           서비스 본체 (취약점 없는 정상 버전). 여기는 수정하지 않는다
├── challenges/    CTF 문제 모음. easy / medium / hard 로 나뉨
├── solution/      문제 풀이. 대회가 끝날 때까지 깃에 올리지 않는다 (.gitignore)
└── docs/          설계 문서 · 팀 가이드
```

## 실행

```bash
cd app
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py                 # http://localhost:8000
```

로그인 계정은 [팀 개발 가이드](docs/TEAM_GUIDE.md) 명세서 6-4절에 있습니다.

자세한 설명과 운영체제별 차이는 [팀 개발 가이드](docs/TEAM_GUIDE.md)를 본다.

## 문제 목록

| 난이도 | 문제 | 출제 | 포트 | 풀이 |
|---|---|---|---|---|
| Easy | [02-records](challenges/easy/02-records) | A조 | 8001 | [solution.md](solution/easy/02-records/solution.md) |
| Easy | [02-portal](challenges/easy/02-portal) | B조 | 8002 | [solution.md](solution/easy/02-portal/solution.md) |
| Easy | [05-staff](challenges/easy/05-staff) | B조 | 8007 | [solution.md](solution/easy/05-staff/solution.md) |
| Easy | [05-gift](challenges/easy/05-gift) | B조 | 8008 | [solution.md](solution/easy/05-gift/solution.md) |
| Medium | [03-party-desk](challenges/medium/03-party-desk) | A조 | 8003 (팀별 8301~) | [solution.md](solution/medium/03-party-desk/solution.md) |
| Medium | [03-review](challenges/medium/03-review) | B조 | 8004 | [solution.md](solution/medium/03-review/solution.md) |
| Medium | [04-mirror](challenges/medium/04-mirror) | B조 | 8006 | [solution.md](solution/medium/04-mirror/solution.md) |
| Medium | [05-deadline](challenges/medium/05-deadline) | A조 | 8005 | [solution.md](solution/medium/05-deadline/solution.md) |
| Hard | [06-ticket](challenges/hard/06-ticket) | A조 | 8009 | [solution.md](solution/hard/06-ticket/solution.md) |
| Hard | [06-santa](challenges/hard/06-santa) | A조 | 8010 | [solution.md](solution/hard/06-santa/solution.md) |
| Hard | [06-convert](challenges/hard/06-convert) | B조 | 8012 | 대회 미사용 |
| Hard | [06-draft](challenges/hard/06-draft) | B조 | 8013 | 대회 미사용 |

전체 목록은 [challenges/README.md](challenges/README.md) 에 있습니다.

## 팀

| 담당 | 이름 | 영역 | 브랜치 |
|---|---|---|---|
| 1 | 정욱 | 공통 레이아웃 · 컴포넌트 · 메인 | `feat/layout-base` |
| 2 | 성원 | 회원가입 · 로그인 · 마이페이지 | `feat/auth` |
| 3 | 수하 | 신청서 작성 · 확인서류 첨부 · 당첨자 조회 | `feat/apply` |
| 4 | 종성 | 운영진 포털 · 당첨 확정 · 관리자 | `feat/admin` |

## 규칙

- 브랜치 구성: `main`(안정판) ← `develop`(작업 통합) ← `feat/...`(개인 작업).
- `main` 과 `develop` 직접 푸시 금지. `feat/...` → Pull Request → 승인 → `develop` 병합.
- `.env`, `instance/`, `uploads/`, `venv/` 는 커밋하지 않는다. 플래그가 공개된다.
- 커밋 전에 `git status` 로 위 항목이 안 뜨는지 확인한다.
- 공통 파일(`base.html`, `style.css`, `app.py`)은 담당자를 통해 수정한다.
