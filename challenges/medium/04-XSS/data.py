from config_flags import secret

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


USERS = {
    "applicant01": {"id": 1,  "password": "test1234", "name": "이정욱",   "role": "applicant",
                    "email": "applicant01@example.com"},
    "applicant02": {"id": 7,  "password": "s3cr3t",   "name": "정민호",   "role": "applicant",
                    "email": "applicant02@example.com"},
    "reviewer":    {"id": 99, "password": secret("ADMIN_PASSWORD"), "name": "운영진", "role": "admin",
                    "email": secret("ADMIN_EMAIL")},
}


APPLICATIONS = {
    41: {
        "id": 41, "user_id": 1, "applicant_name": "이정욱",
        "school": "글래스하우스", "major": "일반석",
        "intro": "매년 가족과 함께 크리스마스 파티에 참석해 왔습니다.",
        "status": "submitted",
        "document": None, "reason": "",
    },
    42: {
        "id": 42, "user_id": 1, "applicant_name": "이정욱",
        "school": "스노우하우스", "major": "VIP석",
        "intro": "친구들과 특별한 연말을 보내고 싶습니다.",
        "status": "draft",
        "document": None, "reason": "",
    },
    43: {
        "id": 43, "user_id": 7, "applicant_name": "정민호",
        "school": "미러하우스", "major": "일반석",
        "intro": "정보보호 동아리에서 웹 해킹을 공부하고 있습니다.",
        "status": "submitted",
        "document": None, "reason": "",
    },
}


def find_user_by_id(user_id):
    for username, u in USERS.items():
        if u["id"] == user_id:
            return dict(u, username=username)
    return None


def next_application_id():
    return max(APPLICATIONS) + 1 if APPLICATIONS else 1
