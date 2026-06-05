from core.agent import agent_reply
from core.user_store import get_user, save_user


def handle_message(phone: str, message: str) -> str:
    user = get_user(phone)

    # ── Onboarding: collect program and level ─────────────────────────────
    if not user:
        if "computer science" in message.lower() and "300" in message:
            save_user(phone, "Computer Science", "300")
            return "Got it! I'll remember that you're a Computer Science Level 300 student. You can now ask about your classes and events!"

        return "Welcome to the BUCC AI Assistant! 👋\n\nPlease tell me your program and level so I can personalise your experience.\n\nExample: Computer Science 300"

    program = user["program"]
    level = user["level"]

    # ── Pass message to AI agent ──────────────────────────────────────────
    return agent_reply(message, program, level)