#!/bin/sh
# 참가자에게 나눠 줄 문제 zip 을 dist/ 에 만듭니다.
#
#   ./scripts/make_zips.sh
#
# 깃이 관리하는 파일만 넣습니다. .env, 서명 키, vault/, 플래그 파일은 .gitignore 에 있어서 들어가지 않습니다.
# 운영진만 쓰는 teams.sh 는 뺍니다. 풀이(solution/)는 문제 폴더 밖이라 들어가지 않습니다.
set -e
cd "$(dirname "$0")/.."
mkdir -p dist
rm -f dist/chal-*.zip

pack() {
  level=$1
  name=$2
  port=$3
  out="$PWD/dist/chal-$port.zip"
  (cd "challenges/$level" && git ls-files -- "$name" ":(exclude)$name/teams.sh" | zip -q -X "$out" -@)
  echo "dist/chal-$port.zip  <-  challenges/$level/$name"
}

pack easy   02-records    8001
pack easy   02-portal     8002
pack medium 03-party-desk 8003
pack medium 03-review     8004
pack medium 05-deadline   8005
pack medium 04-mirror     8006
pack easy   05-staff      8007
pack easy   05-gift       8008
pack hard   06-ticket     8010
pack hard   06-santa      8013
