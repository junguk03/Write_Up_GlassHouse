"""
공유 데이터

데이터베이스는 쓰지 않습니다. 이 파일의 변수가 저장소 역할을 합니다.
서버를 껐다 켜면 처음 상태로 돌아갑니다.

이 문제는 참가자가 회원가입으로 계정을 만들어 시작하므로 고정 신청서가 없습니다.
"""
import itertools

from config_flags import secret

# ---------------------------------------------------------------------------
# 사이트 공통 정보
# ---------------------------------------------------------------------------
SITE = {
    "name": "글래스하우스 크리스마스 파티",
    "recruit_title": "2026 크리스마스 파티 초대권 신청",
    "period_start": "2026-10-20",
    "period_end": "2026-11-07",
    "days_left": 22,
    "contact_tel": "02-123-4567",
    "contact_email": "admission@glasshouse.ac.kr",
    "office_hours": "평일 09:00 - 18:00 (점심시간 12:00 - 13:00)",
}


# ---------------------------------------------------------------------------
# 로그인 계정  (운영진 + 회원가입으로 만든 계정)
#   키   = 아이디
#   id   = 사용자 번호.  신청서의 user_id 와 짝이 맞습니다.
#   role = applicant 또는 admin.  회원가입 계정은 항상 applicant 입니다.
#   email = 비밀번호 찾기에 씁니다
#
# 소스가 공개되므로 관리자 비밀번호와 이메일은 .env 에서 읽습니다.
# ---------------------------------------------------------------------------
USERS = {
    "reviewer": {"id": 99, "password": secret("ADMIN_PASSWORD"), "name": "운영진", "role": "admin",
                 "email": secret("ADMIN_EMAIL")},
}


# ---------------------------------------------------------------------------
# 신청서
#   id              신청서 번호
#   user_id         이 신청서의 주인
#   applicant_name  신청자 이름
#   school / major  소속 · 희망 좌석
#   intro           신청 사연
#   status          draft / submitted / reviewing / accepted / rejected
# ---------------------------------------------------------------------------
APPLICATIONS = {}


# ---------------------------------------------------------------------------
# 도우미
# ---------------------------------------------------------------------------
def find_user_by_id(user_id):
    """사용자 번호로 계정을 찾습니다. 없으면 None 을 돌려줍니다."""
    for username, u in USERS.items():
        if u["id"] == user_id:
            return dict(u, username=username)
    return None


_application_ids = itertools.count(1)


def next_application_id():
    """새 신청서에 쓸 번호를 돌려줍니다."""
    return next(_application_ids)


# 회원가입 계정 번호는 100 부터 씁니다. 운영진(99)과 겹치지 않습니다.
_user_ids = itertools.count(100)


def next_user_id():
    """회원가입한 새 계정에 쓸 번호를 돌려줍니다."""
    return next(_user_ids)
