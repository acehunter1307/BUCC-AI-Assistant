from datetime import date
from core.loader import load_json

_raw_updates = load_json("data/updates/whatsapp_updates.json")
UPDATES = _raw_updates["updates"]

def update_applies(update: dict, target_date: date) -> bool:
    start = date.fromisoformat(update["applies_on"])
    end = (
        date.fromisoformat(update["applies_until"])
        if update["applies_until"]
        else start
    )
    return start <= target_date <= end

CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}

def sort_updates(updates: list) -> list:
    return sorted(
        updates,
        key=lambda u: (
            u["applies_until"] is not None,          # more specific first
            u["created_at"],                         # newer last
            CONFIDENCE_RANK[u["confidence"]]
        ),
        reverse=True
    )

def apply_update(record: dict, update: dict) -> dict:
    resolved = record.copy()

    utype = update["update_type"]
    change = update["change"]

    if utype == "time_change":
        resolved["start_time"] = change["new"]["start_time"]
        resolved["end_time"] = change["new"]["end_time"]

    elif utype == "venue_change":
        resolved["location"] = change["new"]["location"]

    elif utype in ("class_cancelled", "event_cancelled"):
        resolved["status"] = "cancelled"

    resolved["_overridden_by"] = update["update_id"]
    return resolved

def resolve_record(record: dict, target_date: date) -> dict:
    assert isinstance(record, dict), f"Expected dict, got {type(record)}"
    applicable = []
    for u in UPDATES:
        assert isinstance(u, dict), f"Update is not dict: {u}"
        if u["target_id"] == record.get("class_id", record.get("event_id")):
            if update_applies(u, target_date):
                applicable.append(u)

    resolved = record.copy()

    for update in sort_updates(applicable):
        resolved = apply_update(resolved, update)

    return resolved

