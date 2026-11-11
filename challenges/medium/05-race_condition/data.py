"""
공유 데이터

데이터베이스는 쓰지 않습니다. 이 파일의 변수가 저장소 역할을 합니다.
서버를 껐다 켜면 처음 상태로 돌아갑니다.

이 문제는 참가자가 회원가입으로 계정을 만들어 시작하므로 고정 원서가 없습니다.
"""
import itertools

from config_flags import secret

# ---------------------------------------------------------------------------
# 사이트 공통 정보
# ---------------------------------------------------------------------------
SITE = {
    "name": "글래스하우스 정보보호학과",
    "recruit_title": "2026학년도 신입생 수시 원서 접수",
    "period_start": "2026-10-20",
    "period_end": "2026-11-07",
    "days_left": 22,
    "contact_tel": "02-123-4567",
    "contact_email": "admission@glasshouse.ac.kr",
    "office_hours": "평일 09:00 - 18:00 (점심시간 12:00 - 13:00)",
}


# ---------------------------------------------------------------------------
# 로그인 계정  (심사위원 + 회원가입으로 만든 계정)
#   키   = 아이디
#   id   = 사용자 번호.  원서의 user_id 와 짝이 맞습니다.
#   role = applicant 또는 admin.  회원가입 계정은 항상 applicant 입니다.
#   email = 비밀번호 찾기에 씁니다
#
# 소스가 공개되므로 관리자 비밀번호와 이메일은 .env 에서 읽습니다.
# ---------------------------------------------------------------------------
USERS = {
    "reviewer": {"id": 99, "password": secret("ADMIN_PASSWORD"), "name": "심사위원", "role": "admin",
                 "email": secret("ADMIN_EMAIL")},
}


# ---------------------------------------------------------------------------
# 원서
#   id              원서 번호
#   user_id         이 원서의 주인
#   applicant_name  지원자 이름
#   school / major  출신 학교 · 지원 학과
#   intro           자기소개
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
    """새 원서에 쓸 번호를 돌려줍니다."""
    return next(_application_ids)


# 회원가입 계정 번호는 100 부터 씁니다. 심사위원(99)과 겹치지 않습니다.
_user_ids = itertools.count(100)


def next_user_id():
    """회원가입한 새 계정에 쓸 번호를 돌려줍니다."""
    return next(_user_ids)
