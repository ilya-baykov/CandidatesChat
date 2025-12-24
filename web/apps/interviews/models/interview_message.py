from django.db import models
from django.utils import timezone

from . import InterviewQuestion
from .interview import Interview

from ...reference.models import MessageRole

class InterviewMessage(models.Model):
    """
    Лог сообщений в рамках интервью.
    """

    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    question = models.ForeignKey(
        InterviewQuestion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
        help_text="Вопрос, к которому относится сообщение (если применимо)",
    )

    role = models.ForeignKey(
        MessageRole,
        on_delete=models.PROTECT,
        help_text="Роль отправителя сообщения",
    )

    content = models.TextField(help_text="Текст сообщения")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["interview", "created_at"]),
            models.Index(fields=["question", "created_at"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"[{self.role.code}] {self.content[:50]}..."