import itertools

from config_flags import flag, secret


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


USERS = {
    "reviewer": {"id": 99, "password": secret("ADMIN_PASSWORD"), "name": "심사위원", "role": "admin"},
}


APPLICATIONS = {
    50: {
        "id": 50, "user_id": 8, "applicant_name": "flag",
        "school": "Flag!!", "major": flag("FLAG_IDOR"),
        "intro": "SUCCESS Find FLAGG",
        "status": "submitted",
    },
}


def find_user_by_id(user_id):
    for username, u in USERS.items():
        if u["id"] == user_id:
            return dict(u, username=username)
    return None


def next_application_id():
    return max(APPLICATIONS) + 1 if APPLICATIONS else 1


# 회원가입 계정 번호는 100 부터 씁니다.
_user_ids = itertools.count(100)


def next_user_id():
    """회원가입한 새 계정에 쓸 번호를 돌려줍니다."""
    return next(_user_ids)
