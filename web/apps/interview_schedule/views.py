from __future__ import annotations

import json
import logging
from datetime import datetime

import pytz
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views import View

from config.settings.base import TIME_ZONE
from apps.interviews.models import Interview
from core.integrations.oko.repositories.candidate_repository import OkoCandidateRepository
from core.integrations.oko.repositories.vacancy_repository import OkoVacancyRepository
from .forms import BookSlotForm
from .models import InterviewSlot
from .services.slot_generator import SlotGenerator
from .tasks.triggers import start_send_calendar_invite

logger = logging.getLogger(__name__)


class ScheduleView(View):
    _slot_generator = SlotGenerator()
    _tz = pytz.timezone(TIME_ZONE)
    template_name = "interview_schedule/schedule.html"

    def _get_interview_context(self, token: str) -> tuple[str, str, str]:
        """
        По токену достаём кандидата и рекрутера из БД.
        Возвращает (candidate_email, candidate_name, recruiter_email).
        Бросает Http404 если что-то не найдено.
        """
        interview = get_object_or_404(Interview, token=token)

        candidate = OkoCandidateRepository.get_by_id(interview.candidate_id)
        if not candidate:
            logger.error(
                "Кандидат не найден в ОКО | candidate_id=%s | token=%s",
                interview.candidate_id, token,
            )
            raise Http404("Кандидат не найден")

        vacancy = OkoVacancyRepository.get_by_id(interview.vacancy_id)
        if not vacancy:
            logger.error(
                "Вакансия не найдена в ОКО | vacancy_id=%s | token=%s",
                interview.vacancy_id, token,
            )
            raise Http404("Вакансия не найдена")

        recruiter_email = vacancy["email_recruiter"]
        if not recruiter_email:
            logger.error(
                "Email рекрутера пустой | vacancy_id=%s | token=%s",
                interview.vacancy_id, token,
            )
            raise Http404("Email рекрутера не задан")

        return candidate["email_address"], candidate["full_name"], recruiter_email

    def get(self, request, token):
        candidate_email, candidate_name, recruiter_email = self._get_interview_context(token)

        slots = self._slot_generator.generate(weeks=2)
        form = BookSlotForm(initial={"candidate_email": candidate_email})

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
            "recruiter_email": recruiter_email,
            "candidate_email": candidate_email,
            "candidate_name": candidate_name,
            "token": token,
        }
        return render(request, self.template_name, context)

    def post(self, request, token):
        candidate_email, candidate_name, recruiter_email = self._get_interview_context(token)

        form = BookSlotForm(request.POST)
        if not form.is_valid():
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)

        slot_dt: datetime = form.cleaned_data["slot"]
        candidate_email = form.cleaned_data["candidate_email"]  # кандидат мог изменить
        comment: str = form.cleaned_data["comment"]

        interview_slot = InterviewSlot.objects.create(
            candidate_email=candidate_email,
            candidate_name=candidate_name,
            recruiter_email=recruiter_email,
            start_datetime=slot_dt,
            duration_minutes=60,
        )

        start_send_calendar_invite(
            interview_id=interview_slot.pk,
            candidate_email=candidate_email,
            candidate_name=candidate_name,
            recruiter_email=recruiter_email,
            start=slot_dt,
        )

        local_dt = slot_dt.astimezone(self._tz)

        return JsonResponse(
            {
                "ok": True,
                "message": "Приглашение отправлено!",
                "slot_label": local_dt.strftime("%d %B %Y, %H:%M МСК"),
                "invite_sent": True,
            }
        )
