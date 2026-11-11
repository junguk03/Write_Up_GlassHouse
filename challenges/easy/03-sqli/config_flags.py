"""
.env 읽기

플래그와 관리자 비밀번호처럼 공개되면 안 되는 값은 코드에 직접 쓰지 않고
.env 파일에서 읽어옵니다. .env 는 .gitignore 에 등록되어 있어 깃허브에 올라가지 않습니다.
그래서 소스를 공개해도 이 값들은 노출되지 않습니다.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def flag(name, default="GlassHouse{dummy_flag_not_set}"):
    """.env 가 없어도 앱이 죽지 않도록 더미 값을 돌려줍니다."""
    return os.environ.get(name, default)


def secret(name):
    """
    비밀번호처럼 알면 바로 뚫리는 값을 읽습니다.
    .env 에 없으면 None 을 돌려주므로, 그 계정은 어떤 비밀번호로도 로그인되지 않습니다.
    """
    return os.environ.get(name)
