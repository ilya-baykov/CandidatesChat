from __future__ import annotations
import pytz
import json
import logging
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from .forms import BookSlotForm
from .models import InterviewSlot
from .services.meeting_slot_creator import generate_slots, slots_by_week, send_calendar_invite

logger = logging.getLogger(__name__)

RECRUITER_EMAIL = "recruiter@example.com"  # TODO: move to settings / env
TIMEZONE = "Europe/Moscow"


class ScheduleView(View):
    template_name = "interview_schedul/schedule.html"

    def get(self, request):
        slots = generate_slots(weeks=2)
        grouped = slots_by_week(slots)
        form = BookSlotForm()

        tz = pytz.timezone(TIMEZONE)
        slots_json = [
            {
                "iso": s.isoformat(),
                "date": s.astimezone(tz).strftime("%Y-%m-%d"),
                "time": s.astimezone(tz).strftime("%H:%M"),
                "label": s.astimezone(tz).strftime("%d %b, %H:%M"),
            }
            for s in slots
        ]

        context = {
            "form": form,
            "slots_json": json.dumps(slots_json, ensure_ascii=False),
            "recruiter_email": RECRUITER_EMAIL,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = BookSlotForm(request.POST)
        if not form.is_valid():
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)

        slot_dt: datetime = form.cleaned_data["slot"]
        candidate_email: str = form.cleaned_data["candidate_email"]
        candidate_name: str = form.cleaned_data["candidate_name"]

        # Persist booking
        interview = InterviewSlot.objects.create(
            candidate_email=candidate_email,
            candidate_name=candidate_name,
            recruiter_email=RECRUITER_EMAIL,
            start_datetime=slot_dt,
            duration_minutes=60,
        )

        # Send calendar invite (best-effort)
        msg_id = send_calendar_invite(
            candidate_email=candidate_email,
            candidate_name=candidate_name,
            recruiter_email=RECRUITER_EMAIL,
            start=slot_dt,
        )
        if msg_id:
            interview.gmail_message_id = msg_id
            interview.status = InterviewSlot.STATUS_CONFIRMED
            interview.save(update_fields=["gmail_message_id", "status"])

        tz = pytz.timezone(TIMEZONE)
        local_dt = slot_dt.astimezone(tz)

        return JsonResponse(
            {
                "ok": True,
                "message": "Приглашение отправлено!",
                "slot_label": local_dt.strftime("%d %B %Y, %H:%M МСК"),
                "invite_sent": bool(msg_id),
            }
        )


class SuccessView(View):
    template_name = "interviews/success.html"

    def get(self, request):
        return render(request, self.template_name)
