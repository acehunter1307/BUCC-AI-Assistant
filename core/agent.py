from anthropic import Anthropic
from core.retrieval import (
    get_classes_today,
    get_classes_this_week,
    get_next_class,
    get_events_today,
    get_events_this_week,
    get_class_duration,
)

client = Anthropic()

TOOLS = [
    {
        "name": "get_classes_today",
        "description": "Get today's classes for a student",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_classes_this_week",
        "description": "Get this week's classes for a student",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_events_this_week",
        "description": "Get events happening this week",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_next_class",
        "description": "Get the next upcoming class",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_class_duration",
        "description": "Get the duration of a specific class",
        "input_schema": {
            "type": "object",
            "properties": {
                "class_name": {
                    "type": "string"
                }
            }
        }
    },
    {
        "name": "get_events_today",
        "description": "Get events happening today",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]


def agent_reply(message, program, level):

    response = client.messages.create(
        model="claude-3-5-sonnet",
        max_tokens=200,
        tools=TOOLS,
        messages=[{"role": "user", "content": message}]
    )

    action = None

    for block in response.content:
        if block.type == "tool_use":
            action = block
            break

    if not action:
        return "Sorry, I couldn't understand the request."

    if action.name == "get_classes_today":
        return str(get_classes_today(program, level))

    if action.name == "get_classes_this_week":
        return str(get_classes_this_week(program, level))

    if action.name == "get_events_this_week":
        return str(get_events_this_week(level))

    if action.name == "get_class_duration":
        class_name = action.input.get("class_name")
        return str(get_class_duration(program, level, class_name))

    if action.name == "get_next_class":
        return str(get_next_class(program, level))

    if action.name == "get_events_today":
        return str(get_events_today(level))
