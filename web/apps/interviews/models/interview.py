import uuid

from django.db import models

from ...reference.models import InterviewStatus


class Interview(models.Model):
    """
    Корневая модель интервью.
    Один кандидат + одна вакансия = один диалог.
    """

    candidate_id = models.UUIDField(db_index=True)  # id кандидата (из БД ОКО)
    vacancy_id = models.UUIDField(db_index=True)  # id вакансии (из БД ОКО)

    status = models.ForeignKey(InterviewStatus, on_delete=models.CASCADE, help_text="Статус интервью")
    token = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4,
                             help_text="Уникальная ссылка для доступа кандидата")

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_score = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Интервью"
        verbose_name_plural = "Интервью"
        unique_together = ["candidate_id", "vacancy_id"]
        indexes = [
            models.Index(fields=["token"]),
        ]

    def __str__(self):
        return f"Интервью #{self.pk} для кандидата с id={self.candidate_id} vacancy_id={self.vacancy_id}"
