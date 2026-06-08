import os
from google import genai
from google.genai import types
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

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
MODEL = "gemini-2.5-flash"

# ── Tool definitions ───────────────────────────────────────────────────────
TOOLS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="get_classes_today",
            description="Get the list of classes scheduled for today for the student.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="get_classes_this_week",
            description="Get all classes scheduled for this week for the student.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="get_next_class",
            description="Get the next upcoming class for the student.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="get_events_today",
            description="Get events happening today at the university.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="get_events_this_week",
            description="Get all events happening this week at the university.",
            parameters=types.Schema(type=types.Type.OBJECT, properties={})
        ),
        types.FunctionDeclaration(
            name="get_class_duration",
            description="Get the duration in minutes of a specific class by its course code or name.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "class_name": types.Schema(
                        type=types.Type.STRING,
                        description="The course code or name e.g. CSC 309, Machine Learning"
                    )
                },
                required=["class_name"]
            )
        ),
    ])
]

SYSTEM_PROMPT = """You are the BUCC AI Assistant, a helpful academic assistant for students at 
Babcock University Computer Science department.

You help students with:
- Their class schedules (today, this week, next class)
- University events (today and this week)
- Class durations

Always use the available tools to fetch real data before responding.
Keep responses friendly, concise and conversational.
If a student asks something you cannot answer with the available tools, 
politely let them know what you can help with.
Do not make up class times, locations, or events."""


def call_tool(name: str, arguments: dict, program: str, level: str) -> str:
    """Execute the tool Gemini decided to call and return formatted result."""
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
    """Send message to Gemini, handle tool call, return natural response.
    Falls back to rule-based query_router if Gemini is unavailable.
    """

    if not GOOGLE_API_KEY:
        return _fallback(message, program, level)

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)

        # ── First call: let Gemini decide which tool to use ────────────────
        response = client.models.generate_content(
            model=MODEL,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=TOOLS,
                tool_config=types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(
                        mode=types.FunctionCallingConfigMode.AUTO
                    )
                ),
            ),
        )

        # ── Check if Gemini wants to call a tool ───────────────────────────
        for part in response.candidates[0].content.parts:
            if part.function_call:
                fn = part.function_call
                tool_name = fn.name
                tool_args = dict(fn.args) if fn.args else {}

                print(f"DEBUG tool call: {tool_name} args: {tool_args}")

                # Execute the tool
                tool_result = call_tool(tool_name, tool_args, program, level)

                # ── Second call: send tool result back to Gemini ───────────
                response2 = client.models.generate_content(
                    model=MODEL,
                    contents=[
                        types.Content(role="user", parts=[types.Part(text=message)]),
                        types.Content(role="model", parts=[types.Part(function_call=fn)]),
                        types.Content(role="user", parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    response={"result": tool_result}
                                )
                            )
                        ]),
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                    ),
                )
                return response2.text.strip()

        # ── Gemini replied directly without a tool call ────────────────────
        text = response.text.strip() if response.text else ""
        if not text:
            return _fallback(message, program, level)
        return text

    except Exception as e:
        print(f"Gemini error: {e}")
        return _fallback(message, program, level)