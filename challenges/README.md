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

`docs/CTF_WORKFLOW.md` 를 보십시오. 요약하면 이렇습니다.

```bash
git checkout develop && git pull origin develop

mkdir -p challenges/easy/02-bac
rsync -a --exclude venv --exclude __pycache__ --exclude .env --exclude '*.pyc' \
      app/ challenges/easy/02-bac/

# 1. 검사하는 줄을 지우거나 변형해 취약하게 만듭니다
# 2. config_flags.py 를 통해 플래그를 심습니다
# 3. cp .env.example .env 후 실제 플래그를 적습니다
```

`solution/` 은 상대 조가 다 푼 뒤에 추가합니다.
그래서 문제는 만들자마자 `develop` 에 병합해도 답이 새지 않습니다.
