from fastapi import APIRouter, Query
from fastapi import Request
from starlette.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from core.agent import agent_reply
from core.chat_service import handle_message
from core.user_store import get_user, save_user
from core.query_router import route_query
from core.retrieval import (
    get_classes_today,
    get_next_class,
    get_events_today,
    get_events_this_week,
)

router = APIRouter()


@router.get("/classes/today")
def classes_today(
    program: str = Query(...),
    level: str = Query(...)
):
    return get_classes_today(program, level)


@router.get("/classes/next")
def next_class(
    program: str = Query(...),
    level: str = Query(...)
):
    return get_next_class(program, level)


@router.get("/events/today")
def events_today():
    return get_events_today()


@router.get("/events/week")
def events_this_week():
    return get_events_this_week()


# ── AI-powered ask endpoint ────────────────────────────────────────────────
@router.get("/ask")
def ask(
    q: str,
    program: str,
    level: str
):
    reply = agent_reply(q, program, level)
    return {"text": reply}
 

## WhatsApp webhook endpoint for Twilio integration

@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()

    phone = form.get("From")
    message = form.get("Body", "").lower()

    reply = handle_message(phone, message)

    resp = MessagingResponse()
    resp.message(reply)

    return Response(content=str(resp), media_type="application/xml")