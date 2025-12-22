from django.db import models
from django.utils import timezone
from web.apps.interviews.models.interview import Interview
from web.apps.reference.models.interview import MessageRole


class InterviewMessage(models.Model):
    """
    Лог сообщений в рамках интервью.
    Сохраняет все сообщения от кандидата, ИИ-агента и системы.
    """
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name="messages")
    role = models.ForeignKey(
        MessageRole,
        on_delete=models.PROTECT,
        help_text="Роль отправителя сообщения (кандидат, ИИ-агент, система)"
    )
    content = models.TextField(help_text="Текст сообщения")
    created_at = models.DateTimeField(default=timezone.now, help_text="Время создания сообщения")

    class Meta:
        verbose_name = "Сообщение интервью"
        verbose_name_plural = "Сообщения интервью"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["interview", "created_at"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"[{self.role.title}] {self.content[:50]}..."
