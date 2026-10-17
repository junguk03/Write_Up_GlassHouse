"""
공유 데이터

데이터베이스는 쓰지 않습니다. 이 파일의 변수가 저장소 역할을 합니다.
서버를 껐다 켜면 처음 상태로 돌아갑니다.

네 명이 모두 이 파일을 읽어 쓰므로 **구조를 바꾸지 마십시오.**
항목을 추가해야 하면 정욱에게 말해 주십시오.
"""

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
# 로그인 계정  (회원가입 없이 미리 정해 둔 계정만 사용합니다)
#   키   = 아이디
#   id   = 사용자 번호.  원서의 user_id 와 짝이 맞습니다.
#   role = applicant 또는 admin
# ---------------------------------------------------------------------------
USERS = {
    "applicant01": {"id": 1,  "password": "test1234", "name": "이정욱",   "role": "applicant"},
    "applicant02": {"id": 7,  "password": "s3cr3t",   "name": "정민호",   "role": "applicant"},
    "reviewer":    {"id": 99, "password": "adminpw",  "name": "심사위원", "role": "admin"},
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
APPLICATIONS = {
    41: {
        "id": 41, "user_id": 1, "applicant_name": "이정욱",
        "school": "글래스고등학교", "major": "정보보호학과",
        "intro": "보안에 관심이 많아 3년간 동아리에서 활동했습니다.",
        "status": "submitted",
    },
    42: {
        "id": 42, "user_id": 1, "applicant_name": "이정욱",
        "school": "하우스고등학교", "major": "컴퓨터공학과",
        "intro": "웹 서비스를 직접 만들어 본 경험이 있습니다.",
        "status": "draft",
    },
    43: {
        "id": 43, "user_id": 7, "applicant_name": "정민호",
        "school": "미러고등학교", "major": "정보보호학과",
        "intro": "다른 사람의 원서입니다. applicant01 에게는 보이면 안 됩니다.",
        "status": "submitted",
    },
}


# ---------------------------------------------------------------------------
# 도우미
# ---------------------------------------------------------------------------
def find_user_by_id(user_id):
    """사용자 번호로 계정을 찾습니다. 없으면 None 을 돌려줍니다."""
    for username, u in USERS.items():
        if u["id"] == user_id:
            return dict(u, username=username)
    return None


def next_application_id():
    """새 원서에 쓸 번호를 돌려줍니다."""
    return max(APPLICATIONS) + 1 if APPLICATIONS else 1
