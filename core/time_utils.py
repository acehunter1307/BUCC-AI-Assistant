from datetime import datetime, date, timedelta, time

def parse_time(t: str) -> time:
    hour, minute = map(int, t.split(":"))
    return time(hour, minute)


def today_info():
    today = date.today()
    weekday = today.strftime("%A")
    return today, weekday