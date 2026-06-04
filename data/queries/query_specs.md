1. What do i have today?

## Query: GET_CLASSES_TODAY

Description:
Return all classes scheduled for today.

Required data:

- timetable.class_id
- timetable.day
- timetable.start_time
- timetable.program
- timetable.level

Logic:

- Determine today's weekday
- Filter classes where day == weekday
- Filter by program and level
- Sort by start_time

Output:

- List of class sessions for the day

2. What events are happening today?

## Query: GET_EVENTS_TODAY

Description:
Return all academic events happening today.

Required data:

- events.event_id
- events.start_date
- events.end_date
- events.levels

Logic:

- today ∈ [start_date, end_date] (inclusive)
- Filter by level if provided

Output:

- List of events for the day

3. What classes am i having this week?

## Query: GET_CLASSES_THIS_WEEK

Description:
Return all classes scheduled for this week.

Requires data:

- timetable.day
- timetable.start_time
- timetable.program
- timetable.level

Logic:

- Compute current week (Monday–Sunday)
- Include all timetable sessions whose day matches any weekday in the week
- Filter by program and level
- Sort by weekday index, then start_time

Output

- List of class sessions for the week

4. What class am i having next?

## Query: GET_NEXT_CLASS

Description:
Return the next class session for the day.

Requires data:

- timetable.day
- timetable.start_time
- timetable.program
- timetable.level

Logic:

- Determine today's weekday and current time
- Filter classes where day == weekday and start_time > current_time
- If none found:
    - Check subsequent weekdays in order
- Filter by program and level
- Return the earliest valid session

Output

- Returns the next immediate class session

5. How long is my BU-CSC307 class?

## Query: GET_CLASS_DURATION_TIME

Description:
Return the duration of the chosen class.

Requires data:
- timetable.course_code
- timetable.duration_minutes
- timetable.program
- timetable.level

Logic:
- Identify the class by course code
- Filter by program and level
- Return duration_minutes

Output

- Returns the duration of the class in minutes
