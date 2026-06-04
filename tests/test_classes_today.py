from datetime import date
from core import retrieval

def test_get_classes_today_basic(monkeypatch):
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

    monkeypatch.setattr(retrieval, "CLASSES", mock_classes)

    monkeypatch.setattr(
        retrieval,
        "today_info",
        lambda: (date(2026, 3, 2), "Monday")
    )

    results = retrieval.get_classes_today("Computer Science", "100")

    assert len(results) == 1
    assert results[0]["course_code"] == "CSC101"