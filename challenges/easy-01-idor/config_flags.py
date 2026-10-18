"""
플래그 읽기

플래그 문자열은 코드에 직접 쓰지 않고 .env 파일에서 읽어옵니다.
.env 는 .gitignore 에 등록되어 있어 깃허브에 올라가지 않습니다.
그래서 소스를 공개해도 플래그는 노출되지 않습니다.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def flag(name, default="GlassHouse{dummy_flag_not_set}"):
    """.env 가 없어도 앱이 죽지 않도록 더미 값을 돌려줍니다."""
    return os.environ.get(name, default)
