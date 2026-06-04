def format_response(intent: str, data):
    if intent == "next_class":
        if not data:
            return "You have no more classes scheduled."

        cls = data
        return (
            f"Your next class is {cls['course_code']} "
            f"from {cls['start_time']} to {cls['end_time']} "
            f"at {cls.get('location', cls.get('venue', 'Unknown location'))}."
        )

    if intent == "classes_today":
        if not data:
            return "You have no classes today."

        lines = ["Here are your classes today:"]
        for cls in data:
            lines.append(
                f"- {cls['course_code']} "
                f"({cls['start_time']} – {cls['end_time']}) "
                f"at {cls.get('location', cls.get('venue', 'Unknown location'))}"
            )
        return "\n".join(lines)

    if intent == "events_today":
        if not data:
            return "There are no events today."

        lines = ["Events happening today:"]
        for e in data:
            # events may contain start/end dates rather than a single time field
            time_part = e.get('time') or e.get('start_time') or ''
            if not time_part:
                sd = e.get('start_date')
                ed = e.get('end_date')
                if sd and ed and sd != ed:
                    time_part = f"{sd} to {ed}"
                else:
                    time_part = sd or ed or ''
            time_part = f" ({time_part})" if time_part else ''
            lines.append(f"- {e.get('title', 'Untitled')}{time_part}")
        return "\n".join(lines)

    if intent == "events_this_week":
        if not data:
            return "There are no events scheduled this week."

        lines = ["Events this week:"]
        for e in data:
            date_part = e.get('date') or e.get('start_date') or ''
            lines.append(
                f"- {e.get('title', 'Untitled')}{(' on ' + date_part) if date_part else ''}")
        return "\n".join(lines)

    return "Sorry, I don’t understand that question yet."
