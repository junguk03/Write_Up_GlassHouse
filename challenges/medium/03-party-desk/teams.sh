#!/bin/sh
# 03-party-desk 를 팀마다 따로 띄웁니다. 팀 N 은 포트 8300+N 을 씁니다.
#
#   ./teams.sh up 5      팀 1~5 켜기  (8301 ~ 8305)
#   ./teams.sh down 5    팀 1~5 끄기
#
# 팀마다 데이터가 따로라서 한 팀이 비밀번호를 바꿔도 다른 팀에는 영향이 없습니다.
set -e
cd "$(dirname "$0")"

cmd=$1
n=${2:-5}

if [ "$cmd" != up ] && [ "$cmd" != down ]; then
  echo "사용법: ./teams.sh up|down 팀수"
  exit 1
fi

[ "$cmd" = up ] && docker compose build

for i in $(seq 1 "$n"); do
  port=$((8300 + i))
  TEAM_PORT=$port docker compose -p "party-desk-team$i" "$cmd" $([ "$cmd" = up ] && echo -d)
  [ "$cmd" = up ] && echo "팀 $i → 포트 $port"
done
