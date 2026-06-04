from core.query_router import route_query
from core.user_store import get_user, save_user


def handle_message(phone: str, message: str):
    user = get_user(phone)

    # If we don't know the user yet
    if not user:
        if "computer science" in message and "300" in message:
            save_user(phone, "Computer Science", "300")
            return "Got it! I'll remember that. You can now ask about your classes."

        return "Welcome! Please tell me your program and level (e.g. Computer Science 300)."

    program = user["program"]
    level = user["level"]

    result = route_query(message, program, level)

    return result["text"]