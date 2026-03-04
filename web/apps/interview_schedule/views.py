from __future__ import annotations

import json
import logging
from datetime import datetime

import pytz
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from config.settings.base import TIME_ZONE
from .forms import BookSlotForm
from .models import InterviewSlot
from .services.slot_generator import SlotGenerator
from .tasks.triggers import start_send_calendar_invite

logger = logging.getLogger(__name__)

RECRUITER_EMAIL = "iterehofa@gmail.com"  # TODO


class ScheduleView(View):
    _slot_generator = SlotGenerator()
    _tz = pytz.timezone(TIME_ZONE)
    template_name = "interview_schedule/schedule.html"

    def get(self, request):
        slots = self._slot_generator.generate(weeks=2)
        form = BookSlotForm()

        slots_json = [
            {
                "iso": s.isoformat(),
                "date": s.astimezone(self._tz).strftime("%Y-%m-%d"),
                "time": s.astimezone(self._tz).strftime("%H:%M"),
                "label": s.astimezone(self._tz).strftime("%d %b, %H:%M"),
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

        interview = InterviewSlot.objects.create(
            candidate_email=candidate_email,
            candidate_name=candidate_name,
            recruiter_email=RECRUITER_EMAIL,
            start_datetime=slot_dt,
            duration_minutes=60,
        )

        start_send_calendar_invite(
            interview_id=interview.pk,
            candidate_email=candidate_email,
            candidate_name=candidate_name,
            recruiter_email=RECRUITER_EMAIL,
            start=slot_dt,
        )

        local_dt = slot_dt.astimezone(self._tz)

        return JsonResponse(
            {
                "ok": True,
                "message": "Приглашение отправлено!",
                "slot_label": local_dt.strftime("%d %B %Y, %H:%M МСК"),
                "invite_sent": True,  # задача поставлена в очередь — считаем успехом
            }
        )


class SuccessView(View):
    template_name = "interview_schedule/success.html"

    def get(self, request):
        return render(request, self.template_name)