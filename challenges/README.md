# 문제 모음

난이도별로 폴더를 나눕니다. 폴더 이름은 `<번호>-<짧은이름>` 입니다.

```
challenges/
├── easy/      단일 취약점. 한 단계로 플래그에 닿습니다
├── medium/    두세 개를 엮어야 합니다
└── hard/      세 개 이상, 또는 별도 인프라가 필요합니다
```

## 문제 목록

| 난이도 | 폴더 | 취약점 | 출제 | 풀이 |
|---|---|---|---|---|
| Easy | [01-idor](easy/01-idor) | IDOR | (예시) | 미작성 |

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

`solution/` 은 상대 조가 다 푼 뒤에 추가합니다.
그래서 문제는 만들자마자 `develop` 에 병합해도 답이 새지 않습니다.
