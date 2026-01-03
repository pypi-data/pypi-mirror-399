from datetime import datetime


def date_suffix(day: int) -> str:
    if 11 <= day <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def get_accessible_date(date: datetime) -> str:
    return f"Choose {date.strftime('%A')}, {date.strftime('%B')} {date.day}{date_suffix(date.day)}"
