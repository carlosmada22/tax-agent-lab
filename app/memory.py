from sqlitedict import SqliteDict

DB_PATH = "memory.sqlite"


def load_history(user_id: str) -> list[str]:
    with SqliteDict(DB_PATH, autocommit=True) as db:
        return db.get(user_id, [])


def save_history(user_id: str, messages: list[str]) -> None:
    with SqliteDict(DB_PATH, autocommit=True) as db:
        db[user_id] = messages
