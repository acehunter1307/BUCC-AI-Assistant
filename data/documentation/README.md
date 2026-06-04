## School AI Assistant – System Architecture

## Goal:

Answer school-specific questions using private information (events, timetables, announcements) extracted from WhatsApp group messages, calendars and timetables that are not available on the internet.

## Phase 1: The scope

## Decide MVP boundaries

School: BUCC
Department: Computer Science
Data type: announcements + calendar + timetable only
Time range: current semester
Users: students (read-only)

## Ignore for now:

Multiple departments
Real-time WhatsApp syncing
Mobile apps
Voice assistants

## Phase 2: Get the data (1–2 days)

## Step 1: Get permission

Message a group admin and explain:
You’re building a student helper tool
Data will be read-only
No private chats
No names shown
This is important if you ever show this project publicly.

## Step 2: Export WhatsApp chats

From WhatsApp:
Export chat (no media)
Save as .txt or .json
Get data from calendar and timetable

Create a folder "data/raw" to store the raw unprocessed and unnormalized data.

## Phase 3

You are building a system with TWO data sources:

## Authoritative / stable data

School calendar
Official timetable
(what you already have)

## Real-time / dynamic updates

WhatsApp group announcements
Schedule changes
New events, postponements, venue changes

WhatsApp is not your main database — it is your update stream.

## Updated Architecture (with real-time updates)

## Layer 1: Base Knowledge (Stable)

calendar_normalized.json
timetable_normalized.json

Used when:
Nothing has changed
No override exists

## Layer 2: Update Stream (WhatsApp)

WhatsApp messages are parsed into update objects, not events

## Step 0: Folder structure (DO THIS FIRST)

data/
raw/
events.json
timetable.json

normalized/
events_normalized.json
timetable_normalized.json

Rule:

❌ AI never reads from raw/

✅ AI only reads from normalized/

## PART A: Normalize the Academic Calendar (events.json)

## 1️⃣ Define the normalized event schema

Every event should follow this exact shape:

{
"event_id": "evt_2025_08_18_reg_200_600",
"title": "Online Registration",
"description": "Online Registration from Home for 200 Level to 600 Level",
"category": "registration",

"start_date": "2025-08-18",
"end_date": "2025-08-31",
"is_multi_day": true,

"levels": ["200", "300", "400", "500", "600"],
"audience": "students",

"academic_session": "2025/2026",
"source": "official_calendar"
}
This is what makes querying possible.

Normalize dates (CRITICAL) to this:

"start_date": "2025-08-18",
"end_date": "2025-08-31",
"is_multi_day": true

# Always use YYYY-MM-DD

## Event categories

Create a fixed list (don’t overthink it):

## Category Used for

registration | Registration, add/drop
lectures | Classes begin
examination | Tests, exams
holiday | Public holidays
ceremony | Convocation, Founder’s Day
meeting | Senate, Academic Board
break | Semester breaks
orientation | Orientation programs
workshop | Staff / faculty workshops
events | Events
other | Others

## Normalize academic levels

From messy text like:

“200 to 600 Level”
“100 Level & Direct Entry”
“Post-SIWES”

## To:

"levels": ["200", "300", "400", "500", "600"] or: "levels": ["100", "DE"]. If staff only:
"levels": []
"audience": "staff"

## Genreate a stable event 1d

Simple Format:

evt*<year>*<month>\_<short_desc>

## 📅 PART B: Normalize the Timetable (timetable.json)

Flatten each class into its own object
Instead of nesting by day, store classes like this:

{
"class_id": "CSC309_WED_0800",
"course_code": "CSC 309",
"course_name": "Artificial Intelligence",

"day": "Wednesday",
"start_time": "08:00",
"end_time": "10:00",

"location": "BUCODEL Lab 2",
"instructor": "Oladipo",

"program": "Computer Science",
"level": "300",
"semester": "First Semester",

"source": "official_timetable"
}

## Generate class id

<COURSE>_<DAY>_<STARTTIME>

## Add query helpers

Like:
"duration_minutes": 120

## The WhatsApp Update Object (Canonical Schema)

## Goal:

Turn messy WhatsApp announcements into small, precise update objects that your system can trust.

No parsing yet. Just structure and rules.

This is the single schema everything will map to later.

{
"update_id": "upd_2026_03_02_csc309_time_change",
"update_type": "time_change",

"target_type": "class | event",
"target_id": "CSC309_WED_0800",

"applies_on": "2026-03-02",
"applies_until": null,

"change": {
"old": {
"start_time": "08:00",
"end_time": "10:00"
},
"new": {
"start_time": "10:00",
"end_time": "12:00"
}
},

"confidence": "high",
"source": "whatsapp",
"source_group": "CSC 300 Level Group",
"created_at": "2026-03-01T21:14:00Z"
}

## Field-by-field explanation (important)

## update_id

Unique identifier
Used for logging, deletion, expiration

Format:
upd*<date>*<target>\_<type>

## update_type (fixed enum)

time_change
venue_change
class_cancelled
class_added
event_postponed
event_cancelled
event_added

Why this matters:

Logic becomes simple
No guessing during merging

## target_type

class | event

Timetable updates ≠ calendar updates

## target_id

Must match:
class_id (from normalized timetable)
OR
event_id (from normalized calendar)

If it can’t be matched:
Store it as pending
Don’t apply automatically

This avoids corruption.

## applies_on

Date the update is valid
Required

Example:
"applies_on": "2026-03-02"

## applies_until

Optional
Used for multi-day changes

Example:
"applies_until": "2026-03-06"

## change

This is the actual modification.

Time change example:
"change": {
"old": { "start_time": "08:00", "end_time": "10:00" },
"new": { "start_time": "10:00", "end_time": "12:00" }
}

Venue change example:
"change": {
"old": { "location": "BUCODEL Lab 2" },
"new": { "location": "F204" }
}

Cancellation example:
"change": {
"status": "cancelled",
"reason": "Lecturer unavailable"
}

## confidence

high | medium | low

Based on:
Who posted it
Whether it matches official data
Whether multiple messages confirm it

Later, you can say:
“This information was from a class rep (unverified).”

## source

"source": "whatsapp"

## source_group

"source_group": "CSC 300 Level Group"

Never store phone numbers

## created_at

ISO timestamp of the message.
Used for:
Conflict resolution
“Latest update wins”

## 🧠 Special cases (important)

1️⃣ Update affects ALL sessions of a course

Example:

“All CSC 301 classes cancelled today”

Do this:
"target_id": "CSC301",
"target_type": "course"

Then apply to all matching class_ids for that date.
(Advanced but very useful.)

2️⃣ Update can’t find a target
Example:
“AI class moved”
But no class_id matches.

Action:
Store update as unresolved
Flag for manual review
Do NOT apply automatically
