"""
로그인용 사용자 조회 (SQLite).
"""
import sqlite3

import data


def vulnerable_login(username, password):
    # data.USERS 를 임시 메모리 DB 로 옮긴다 (요청마다 새로)
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE users (id INTEGER, username TEXT, password TEXT, "
        "name TEXT, role TEXT, email TEXT)"
    )
    for uname, u in data.USERS.items():
        conn.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
            (u["id"], uname, u["password"], u["name"], u["role"], u.get("email", "")),
        )

    query = (
        "SELECT id, username, name, role FROM users "
        f"WHERE username = '{username}' AND password = '{password}'"
    )
    row = conn.execute(query).fetchone()
    conn.close()
    return row