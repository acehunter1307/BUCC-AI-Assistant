from core.response_formatter import format_response

def route_query(query: str, program: str, level: str):
    q = query.lower()

    NEXT_CLASS_PATTERNS = [
        "next class",
        "next lecture",
        "my next class",
        "what is my next",
        "when is my next",
        "what class is next",
        "when am i having my next class",
    ]

    TODAY_CLASSES_PATTERNS = [
        "classes today",
        "today classes",
        "today class",
        "what classes are today",
        "what classes do we have today",
        "what class do i have today",
        "what class am i having today",
        "what classes am i having today",
        "what classes do i have today",
        "what class are we having today",
        "what are we having today",
        "what do i have today",
        "my classes today",
    ]

    EVENTS_TODAY_PATTERNS = [
        "events today",
        "today events",
        "what events are today",
        "what events do we have today",
        "what events are happening today",
    ]

    EVENTS_WEEK_PATTERNS = [
        "this week",
        "events this week",
        "what events are this week",
        "what events do we have this week",
        "what events are in store for us this week",
        "week events",
    ]

    def matches(patterns):
        return any(p in q for p in patterns)

    if matches(NEXT_CLASS_PATTERNS):
        from core.retrieval import get_next_class
        result = get_next_class(program, level)
        return {
            "intent": "next_class",
            "text": format_response("next_class", result),
            "data": result
        }

    if matches(TODAY_CLASSES_PATTERNS):
        from core.retrieval import get_classes_today
        result = get_classes_today(program, level)
        return {
            "intent": "classes_today",
            "text": format_response("classes_today", result),
            "data": result
        }

    if matches(EVENTS_TODAY_PATTERNS):
        from core.retrieval import get_events_today
        result = get_events_today()
        return {
            "intent": "events_today",
            "text": format_response("events_today", result),
            "data": result
        }

    if matches(EVENTS_WEEK_PATTERNS):
        from core.retrieval import get_events_this_week
        result = get_events_this_week()
        return {
            "intent": "events_this_week",
            "text": format_response("events_this_week", result),
            "data": result
        }

    return {
        "intent": "unknown",
        "message": "Sorry, I don’t understand that yet."
    }