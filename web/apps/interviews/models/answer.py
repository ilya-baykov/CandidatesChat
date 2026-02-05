from django.db import models
from django.utils import timezone

from .question import InterviewQuestion


class InterviewAnswer(models.Model):
    """
    Ответ кандидата на конкретный вопрос.
    Один ответ = один вопрос.
    """
    interview_question = models.OneToOneField(
        InterviewQuestion,
        on_delete=models.CASCADE,
        related_name="answer",
        help_text="Вопрос, на который дан ответ"
    )
    answer_text = models.TextField(help_text="Текст ответа кандидата")
    score = models.FloatField(null=True, blank=True, help_text="Оценка ответа (будет от ИИ или админа)")
    answered_at = models.DateTimeField(default=timezone.now, help_text="Время ответа")
    attempt_count = models.PositiveIntegerField(default=1, verbose_name="Количество попыток ответа",
                                                help_text="Сколько раз кандидат отправлял ответ на этот вопрос")

    class Meta:
        verbose_name = "Ответ на вопрос"
        verbose_name_plural = "Ответы на вопросы"

    def __str__(self):
        return f"Ответ на вопрос {self.interview_question.order} ({self.answered_at.date()})"
