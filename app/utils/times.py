from datetime import datetime, timezone


def get_now_dt() -> datetime:
    return datetime.now(timezone.utc)

def to_local_time(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("Дата из БД должна содержать информацию о часовом поясе (UTC).")

    return dt.astimezone()