#!/bin/sh
set -e

mkdir -p /srv/internal /srv/uploads

cat > /srv/internal/waitlist.txt <<EOF
2026학년도 신입생 수시 추가 합격자 명단 (대외비)

발표일 전까지 외부 공개를 금지합니다.
명단 열람 확인 코드: ${FLAG_XSS:-GlassHouse{dummy_flag_not_set}}
EOF

exec python app.py
