"""
core/utilities/gmail/ics_builder.py

Сборка .ics (iCalendar) файла по параметрам события.
Не зависит от Django — можно переиспользовать в любом месте проекта.
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytz
from icalendar import Calendar, Event

from apps.interview_schedule.services.dto import EventParams


class ICSBuilder:
    """Собирает .ics файл по параметрам события."""

    def build(self, params: EventParams, organizer_email: str) -> bytes:
        cal = Calendar()
        cal.add("prodid", "-//Calendar Invite Sender//EN")
        cal.add("version", "2.0")
        cal.add("method", "REQUEST")
        cal.add_component(self._build_event(params, organizer_email))
        return cal.to_ical()

    @staticmethod
    def _build_event(params: EventParams, organizer_email: str) -> Event:
        event = Event()
        event.add("uid", str(uuid4()))
        event.add("sequence", 0)
        event.add("summary", params.summary)
        event.add("dtstart", params.start)
        event.add("dtend", params.start + timedelta(minutes=params.duration_minutes))
        event.add("dtstamp", datetime.now(pytz.utc))
        event.add("location", params.location)
        event["organizer"] = f"MAILTO:{organizer_email}"
        event.add(
            "attendee",
            f"MAILTO:{params.recipient_email}",
            parameters={
                "ROLE": "REQ-PARTICIPANT",
                "PARTSTAT": "NEEDS-ACTION",
                "RSVP": "TRUE",
            },
        )
        return event
