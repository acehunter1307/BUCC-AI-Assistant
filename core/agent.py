import os
import json
import requests
from core.retrieval import (
    get_classes_today,
    get_classes_this_week,
    get_next_class,
    get_events_today,
    get_events_this_week,
    get_class_duration,
)
from core.response_formatter import format_response
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/auto"

# ── Tool definitions (OpenAI function-calling format) ──────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_classes_today",
            "description": "Get the list of classes scheduled for today for the student.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_classes_this_week",
            "description": "Get all classes scheduled for this week for the student.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_next_class",
            "description": "Get the next upcoming class for the student.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_events_today",
            "description": "Get events happening today at the university.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_events_this_week",
            "description": "Get all events happening this week at the university.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_class_duration",
            "description": "Get the duration in minutes of a specific class by its course code or name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "The course code or name e.g. CSC 309, Machine Learning"
                    }
                },
                "required": ["class_name"]
            }
        }
    },
]

SYSTEM_PROMPT = """
You are the BUCC AI Assistant, a helpful academic assistant for students at 
Babcock University Computer Science department.

You help students with:
- Their class schedules (today, this week, next class)
- University events (today and this week)
- Class durations

Always use the available tools to fetch real data before responding.
Keep responses friendly, concise and conversational.
If a student asks something you cannot answer with the available tools, 
politely let them know what you can help with.
Do not make up class times, locations, or events.
""".strip()


def call_tool(name: str, arguments: dict, program: str, level: str) -> str:
    """Execute the tool the AI decided to call and return formatted result."""
    if name == "get_classes_today":
        data = get_classes_today(program, level)
        return format_response("classes_today", data)

    if name == "get_classes_this_week":
        data = get_classes_this_week(program, level)
        lines = []
        for day, classes in data.items():
            if classes:
                lines.append(f"\n{day}:")
                for cls in classes:
                    lines.append(
                        f"  - {cls['course_code']} ({cls['start_time']}–{cls['end_time']}) at {cls.get('location', 'TBD')}"
                    )
        return "Here are your classes this week:" + "\n".join(lines) if lines else "No classes found this week."

    if name == "get_next_class":
        data = get_next_class(program, level)
        return format_response("next_class", data)

    if name == "get_events_today":
        data = get_events_today(level)
        return format_response("events_today", data)

    if name == "get_events_this_week":
        data = get_events_this_week(level)
        return format_response("events_this_week", data)

    if name == "get_class_duration":
        class_name = arguments.get("class_name", "")
        duration = get_class_duration(class_name, program, level)
        if duration:
            return f"{class_name} lasts {duration} minutes."
        return f"I couldn't find duration info for {class_name}."

    return "I couldn't find that information."


def _fallback(message: str, program: str, level: str) -> str:
    """Rule-based fallback using query_router when AI is unavailable."""
    from core.query_router import route_query
    result = route_query(message, program, level)
    return result.get("text") or result.get("message", "Sorry, I don't understand that yet.")


def agent_reply(message: str, program: str, level: str) -> str:
    """Send message to OpenRouter, handle tool call, return natural response.
    Falls back to rule-based query_router if OpenRouter is unavailable.
    """

    # ── Guard: if no API key, go straight to fallback ─────────────────────
    if not OPENROUTER_API_KEY:
        return _fallback(message, program, level)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "BUCC AI Assistant",
    }

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]

    # ── First call: let AI decide which tool to use ────────────────────────
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
        "max_tokens": 500,
    }

    try:
        res = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        res.raise_for_status()
        data = res.json()
    except Exception:
        # OpenRouter unreachable — use rule-based fallback
        return _fallback(message, program, level)

    choice = data.get("choices", [{}])[0]
    finish_reason = choice.get("finish_reason")
    ai_message = choice.get("message", {})

    # ── If AI wants to call a tool ─────────────────────────────────────────
    if finish_reason == "tool_calls" and ai_message.get("tool_calls"):
        tool_call = ai_message["tool_calls"][0]
        tool_name = tool_call["function"]["name"]
        try:
            tool_args = json.loads(tool_call["function"].get("arguments", "{}"))
        except json.JSONDecodeError:
            tool_args = {}

        # Execute the tool
        tool_result = call_tool(tool_name, tool_args, program, level)

        # ── Second call: let AI turn the data into a natural response ──────
        messages.append(ai_message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": tool_result,
        })

        followup_payload = {
            "model": MODEL,
            "messages": messages,
            "max_tokens": 500,
        }

        try:
            res2 = requests.post(OPENROUTER_URL, headers=headers, json=followup_payload, timeout=30)
            res2.raise_for_status()
            data2 = res2.json()
            return data2["choices"][0]["message"]["content"].strip()
        except Exception:
            # Second call failed — return raw tool result directly
            return tool_result

    # ── AI replied directly without a tool call ────────────────────────────
    content = ai_message.get("content", "").strip()
    if not content:
        return _fallback(message, program, level)
    return content