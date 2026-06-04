from datetime import date
from core import retrieval, update_engine

def test_time_change(monkeypatch):
    mock_classes = [
        {
            "class_id": "CSC101_MON_0800",
            "course_code": "CSC101",
            "day": "Monday",
            "start_time": "08:00",
            "end_time": "10:00",
            "duration_minutes": 120,
            "program": "Computer Science",
            "level": "100",
            "location": "F101"
        }
    ]

    mock_updates = [
        {
            "update_id": "upd_2",
            "update_type": "time_change",
            "target_type": "class",
            "target_id": "CSC101_MON_0800",
            "applies_on": "2026-03-02",
            "applies_until": None,
            "change": {
                "new": {"start_time": "10:00", "end_time": "12:00"}
            },
            "confidence": "high",
            "created_at": "2026-03-01T11:00:00Z"
        }
    ]

    monkeypatch.setattr(retrieval, "CLASSES", mock_classes)
    monkeypatch.setattr(update_engine, "UPDATES", mock_updates)

    monkeypatch.setattr(
        retrieval,
        "today_info",
        lambda: (date(2026, 3, 2), "Monday")
    )

    result = retrieval.get_classes_today("Computer Science", "100")[0]

    assert result["start_time"] == "10:00"
    assert result["end_time"] == "12:00"