from sqlitedict import SqliteDict

DB_PATH = "profile.sqlite"


def load_profile(user_id: str) -> dict:
    with SqliteDict(DB_PATH, autocommit=True) as db:
        return db.get(user_id, {})


def save_profile(user_id: str, profile: dict) -> None:
    with SqliteDict(DB_PATH, autocommit=True) as db:
        db[user_id] = profile
