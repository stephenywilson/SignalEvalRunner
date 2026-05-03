from datetime import datetime


def utc_now_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_date_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")
