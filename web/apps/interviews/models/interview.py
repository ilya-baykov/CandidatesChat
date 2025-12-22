from django.db import models

from .candidate import Candidate
from .vacancy import Vacancy

from ...reference.models import InterviewStatus


class Interview(models.Model):
    """
    Корневая модель интервью.
    Один кандидат + одна вакансия = один диалог.
    Управляет статусом, токеном доступа и итоговой оценкой.
    """
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="interviews")
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="interviews")
    status = models.ForeignKey(InterviewStatus, on_delete=models.CASCADE, help_text="Статус интервью")
    token_link = models.URLField(help_text="Уникальная ссылка для доступа кандидата")

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_score = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Интервью"
        verbose_name_plural = "Интервью"
        unique_together = ["candidate", "vacancy"]
        indexes = [
            models.Index(fields=["token_link"]),
        ]

    def __str__(self):
        return f"Интервью #{self.pk} — {self.candidate} → {self.vacancy}"
