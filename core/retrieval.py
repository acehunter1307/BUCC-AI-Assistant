
from datetime import datetime, timedelta, date
from core.loader import load_json
from core.time_utils import parse_time, today_info
from core.update_engine import resolve_record
from typing import List, Optional


def program_match(record_program: str, query_program: str) -> bool:
    """Return True if the record_program reasonably matches the query_program.

    This performs a case-insensitive substring check in both directions so
    short codes like "CS" will match "Computer Science" and vice-versa.
    """
    if not record_program or not query_program:
        return False
    rp = str(record_program).lower()
    qp = str(query_program).lower()
    # check substring both ways
    if qp in rp or rp in qp:
        return True
    # check initials/acronym of the record program (e.g., "Computer Science" -> "cs")
    parts = [p for p in record_program.split() if p]
    if parts:
        initials = ''.join(p[0] for p in parts).lower()
        if qp == initials:
            return True
    return False


_raw_events = load_json("data/normalized/events_normalized.json")
EVENTS = _raw_events["events"]
_raw = load_json("data/normalized/timetable_normalized.json")
CLASSES = _raw["classes"]


def get_classes_today(program, level):
    today, weekday = today_info()

    base = [
        cls for cls in CLASSES
        if cls["day"] == weekday
        and program_match(cls.get("program", ""), program)
        and str(cls.get("level", "")) == str(level)
    ]

    resolved = []
    for cls in base:
        r = resolve_record(cls, today)
        if r.get("status") != "cancelled":
            resolved.append(r)

    return sorted(resolved, key=lambda c: parse_time(c["start_time"]))


def get_classes_this_week(program, level):
    today = date.today()

    week = {
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": []
    }

    for cls in CLASSES:
        if program_match(cls.get("program", ""), program) and str(cls.get("level", "")) == str(level):
            if cls["day"] in week:
                r = resolve_record(cls, today)
                if r.get("status") != "cancelled":
                    week[cls["day"]].append(r)

    for day in week:
        week[day].sort(key=lambda c: parse_time(c["start_time"]))

    return week


def get_next_class(program, level):
    now = datetime.now()
    today, weekday = today_info()

    # Check today (already resolved)
    today_classes = get_classes_today(program, level)

    for cls in today_classes:
        if parse_time(cls["start_time"]) > now.time():
            return cls

    # Check upcoming days
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    today_index = weekdays.index(weekday) if weekday in weekdays else -1

    for day in weekdays[today_index + 1:]:
        candidates = [
            cls for cls in CLASSES
            if cls["day"] == day
            and program_match(cls.get("program", ""), program)
            and str(cls.get("level", "")) == str(level)
        ]

        if candidates:
            r = resolve_record(
                sorted(candidates, key=lambda c: parse_time(
                    c["start_time"]))[0],
                today
            )
            if r.get("status") != "cancelled":
                return r

    return None


def get_events_today(level=None):
    today = date.today()
    results = []

    for evt in EVENTS:
        start = date.fromisoformat(evt["start_date"])
        end = date.fromisoformat(evt["end_date"])

        if start <= today <= end:
            r = resolve_record(evt, today)
            if r.get("status") != "cancelled":
                if level is None or level in evt["levels"]:
                    results.append(r)

    return results


def get_events_this_week(level=None):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    results = []

    for evt in EVENTS:
        start = date.fromisoformat(evt["start_date"])
        end = date.fromisoformat(evt["end_date"])

        if start <= end_of_week and end >= start_of_week:
            r = resolve_record(evt, today)
            if r.get("status") != "cancelled":
                if level is None or level in evt["levels"]:
                    results.append(r)

    return results


def get_class_duration(course_code: str, program: str, level: str) -> Optional[int]:
    for cls in CLASSES:
        if (
            cls["course_code"] == course_code
            and program_match(cls.get("program", ""), program)
            and str(cls.get("level", "")) == str(level)
        ):
            return cls["duration_minutes"]

    return None
