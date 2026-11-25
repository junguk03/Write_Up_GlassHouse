# 문제 모음

난이도별로 폴더를 나눕니다. 폴더 이름은 `<주차>-<짧은이름>` 입니다.

```
challenges/
├── easy/      단일 취약점. 한 단계로 플래그에 닿습니다
├── medium/    두세 개를 엮어야 합니다
└── hard/      세 개 이상, 또는 별도 인프라가 필요합니다
```

## 문제 목록

| 난이도 | 문제 | 출제 | 포트 | 풀이 |
|---|---|---|---|---|
| Easy | [02-records](easy/02-records) | A조 | 8001 | [solution.md](../solution/easy/02-records/solution.md) |
| Easy | [02-portal](easy/02-portal) | B조 | 8002 | [solution.md](../solution/easy/02-portal/solution.md) |
| Easy | [05-staff](easy/05-staff) | B조 | 8007 | [solution.md](../solution/easy/05-staff/solution.md) |
| Easy | [05-gift](easy/05-gift) | B조 | 8008 | [solution.md](../solution/easy/05-gift/solution.md) |
| Medium | [03-party-desk](medium/03-party-desk) | A조 | 8003 (팀별 8301~) | [solution.md](../solution/medium/03-party-desk/solution.md) |
| Medium | [03-review](medium/03-review) | B조 | 8004 | [solution.md](../solution/medium/03-review/solution.md) |
| Medium | [04-mirror](medium/04-mirror) | B조 | 8006 | [solution.md](../solution/medium/04-mirror/solution.md) |
| Medium | [05-deadline](medium/05-deadline) | A조 | 8005 | [solution.md](../solution/medium/05-deadline/solution.md) |
| Hard | [06-ticket](hard/06-ticket) | A조 | 8009 | [solution.md](../solution/hard/06-ticket/solution.md) |
| Hard | [06-santa](hard/06-santa) | A조 | 8010 | [solution.md](../solution/hard/06-santa/solution.md) |
| Hard | [06-convert](hard/06-convert) | B조 | 8012 | 대회 미사용 |
| Hard | [06-draft](hard/06-draft) | B조 | 8013 | 대회 미사용 |

## 새 문제 만들기

`docs/CTF_WORKFLOW.md` 를 보십시오. 지킬 약속은 `docs/RULES.md` 에 있습니다. 요약하면 이렇습니다.

```bash
git checkout develop && git pull origin develop

mkdir -p challenges/easy/02-bac
rsync -a --exclude venv --exclude __pycache__ --exclude '*.pyc' \
      app/ challenges/easy/02-bac/

# 1. .env 의 플래그 값 · 변수 이름 · ADMIN_PASSWORD · SECRET_KEY 를 바꿉니다
# 2. 검사하는 줄을 지우거나 변형해 취약하게 만듭니다
# 3. config_flags.py 의 flag() 로 플래그를 심습니다
```

풀이는 `solution/<난이도>/<문제 이름>/` 에 씁니다. `solution/` 은 `.gitignore` 에 들어 있어
대회가 끝날 때까지 깃에 올라가지 않습니다. 그래서 문제는 만들자마자 `develop` 에 병합해도 답이 새지 않습니다.
