from django.db import models

from .interview import Interview
from ...reference.models import AnswerStatus


class InterviewQuestion(models.Model):
    """
    Вопрос в контексте конкретного интервью.
    Один вопрос = один ответ. Порядок важен для flow.
    """
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField(help_text="Текст вопроса")
    status = models.ForeignKey(AnswerStatus, on_delete=models.PROTECT, related_name="questions",
                               help_text="Статус ответа на вопрос")
    order = models.PositiveIntegerField(help_text="Порядок вопроса в интервью")

    class Meta:
        verbose_name = "Вопрос интервью"
        verbose_name_plural = "Вопросы интервью"
        unique_together = ["interview", "order"]
        ordering = ["order"]
        indexes = [
            models.Index(fields=["interview", "status"]),
        ]

    def __str__(self):
        return f"Вопрос {self.order}: {self.question_text[:50]}..."
