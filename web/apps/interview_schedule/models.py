from django.db import models
from django.utils import timezone


class InterviewSlot(models.Model):
    """Represents a booked interview slot."""

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Ожидает подтверждения"),
        (STATUS_CONFIRMED, "Подтверждён"),
        (STATUS_CANCELLED, "Отменён"),
    ]

    candidate_email = models.EmailField("Email кандидата")
    candidate_name = models.CharField("Имя кандидата", max_length=255)
    recruiter_email = models.EmailField("Email рекрутера")
    start_datetime = models.DateTimeField("Начало интервью")
    duration_minutes = models.PositiveIntegerField("Длительность (мин)", default=60)
    location = models.CharField("Место/ссылка", max_length=500, default="Outlook")
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    gmail_message_id = models.CharField(
        "Gmail Message ID", max_length=255, blank=True, null=True
    )
    created_at = models.DateTimeField("Создано", default=timezone.now)

    class Meta:
        verbose_name = "Слот интервью"
        verbose_name_plural = "Слоты интервью"
        ordering = ["start_datetime"]

    def __str__(self):
        return f"{self.candidate_name} — {self.start_datetime:%d.%m.%Y %H:%M}"
