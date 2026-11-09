from config_flags import secret

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
    "applicant01": {"id": 1,  "password": "test1234", "name": "이정욱",   "role": "applicant",
                    "email": "applicant01@example.com"},
    "applicant02": {"id": 7,  "password": "s3cr3t",   "name": "정민호",   "role": "applicant",
                    "email": "applicant02@example.com"},
    "reviewer":    {"id": 99, "password": secret("ADMIN_PASSWORD"), "name": "심사위원", "role": "admin",
                    "email": secret("ADMIN_EMAIL")},
    "subAdmin":    {"id": 50, "password": "subpwd", "name": "부관리자", "role": "staff",
                    "email": "staff@glasshouse.ac.kr"},
}


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
        "intro": "정보보호 동아리에서 웹 해킹을 공부하고 있습니다.",
        "status": "submitted",
    },
    50: {
        "id": 50, "user_id": 50, "applicant_name": "이정욱",
        "school": "글래스고등학교", "major": "정보보호학과",
        "intro": "보안에 관심이 많아 3년간 동아리에서 활동했습니다.",
        "status": "submitted", "email":secret("ADMIN_EMAIL")

    }
}


def find_user_by_id(user_id):
    for username, u in USERS.items():
        if u["id"] == user_id:
            return dict(u, username=username)
    return None


def next_application_id():
    return max(APPLICATIONS) + 1 if APPLICATIONS else 1
