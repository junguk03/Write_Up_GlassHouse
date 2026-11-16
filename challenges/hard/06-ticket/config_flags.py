import os

from dotenv import load_dotenv

load_dotenv()


def flag(name, default="GlassHouse{dummy_flag_not_set}"):
    return os.environ.get(name, default)


def secret(name):
    return os.environ.get(name)
