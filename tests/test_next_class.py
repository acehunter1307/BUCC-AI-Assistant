from datetime import date, datetime
from core import retrieval


def test_get_next_class(monkeypatch):
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
        },
        {
            "class_id": "CSC102_MON_1100",
            "course_code": "CSC102",
            "day": "Monday",
            "start_time": "11:00",
            "end_time": "13:00",
            "duration_minutes": 120,
            "program": "Computer Science",
            "level": "100",
            "location": "F102"
        }
    ]

    monkeypatch.setattr(retrieval, "CLASSES", mock_classes)
    monkeypatch.setattr(
        retrieval,
        "today_info",
        lambda: (date(2026, 3, 2), "Monday")
    )

    # patch datetime with a dummy class since the imported `datetime`
    # is the class itself (immutable) and cannot have attributes reassigned.
    class DummyDateTime:
        @classmethod
        def now(cls):
            # use the imported datetime class to construct a fixed timestamp
            return datetime(2026, 3, 2, 9, 0)

    monkeypatch.setattr(retrieval, "datetime", DummyDateTime)

    result = retrieval.get_next_class("Computer Science", "100")

    assert result["course_code"] == "CSC102"
