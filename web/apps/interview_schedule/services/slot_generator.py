from __future__ import annotations

import logging
from datetime import datetime, time, timedelta

import pytz

from apps.interview_schedule.constants import WORK_START, WORK_DAYS, WORK_END, SLOT_DURATION_MINUTES
from config.settings.base import TIME_ZONE

logger = logging.getLogger(__name__)



class SlotGenerator:
    """
    Генерирует список доступных временных слотов для интервью.

    Пример:
        slots = SlotGenerator().generate(weeks=2)
    """

    def __init__(self,
                 work_start: time = WORK_START,
                 work_end: time = WORK_END,
                 work_days: frozenset[int] = WORK_DAYS,
                 slot_duration_minutes: int = SLOT_DURATION_MINUTES) -> None:
        self._tz = pytz.timezone(TIME_ZONE)
        self._work_start = work_start
        self._work_end = work_end
        self._work_days = work_days
        self._slot_duration = timedelta(minutes=slot_duration_minutes)

    def generate(self, weeks: int = 2) -> list[datetime]:
        """Возвращает все доступные слоты на ближайшие `weeks` недель."""
        now = datetime.now(self._tz)
        current = now.date()
        end_date = current + timedelta(weeks=weeks)
        min_start = now + timedelta(hours=1)

        slots: list[datetime] = []
        while current < end_date:
            if current.weekday() in self._work_days:
                slots.extend(self._day_slots(current, min_start))
            current += timedelta(days=1)
        return slots

    def group_by_week(self, slots: list[datetime]) -> dict[str, dict[str, list[datetime]]]:
        """Группирует слоты по номеру недели и дате."""
        grouped: dict[str, dict[str, list[datetime]]] = {}
        for slot in slots:
            local = slot.astimezone(self._tz)
            week_key = f"Неделя {local.date().isocalendar()[1]}"
            day_key = local.strftime("%Y-%m-%d")
            grouped.setdefault(week_key, {}).setdefault(day_key, []).append(slot)
        return grouped


    def _day_slots(self, day: datetime.date, min_start: datetime) -> list[datetime]:
        slots: list[datetime] = []
        slot_dt = self._tz.localize(datetime.combine(day, self._work_start))
        end_dt = self._tz.localize(datetime.combine(day, self._work_end))
        while slot_dt < end_dt:
            if slot_dt > min_start:
                slots.append(slot_dt)
            slot_dt += self._slot_duration
        return slots
