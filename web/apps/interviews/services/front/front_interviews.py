from typing import Optional

from django.db.models import Min, Max
from datetime import datetime
from ...collections import MessageRoleCodes, FrontDialogueMessage, FrontMessageRoleCodes, MessageDates
from ...models import Interview, InterviewMessage


class FrontMessageService:

    @staticmethod
    def get_dialogue_history(interview: Interview) -> list[FrontDialogueMessage]:
        """
        Формирует полную историю диалога интервью в формате, готовом для фронтенда.

        Особенности:
        - SYSTEM и AGENT объединяются в одну роль "assistant"
        """
        messages = (
            InterviewMessage.objects
            .filter(interview=interview)
            .select_related("role")
            .order_by("created_at")
        )

        history: list[FrontDialogueMessage] = []

        for msg in messages.iterator():  # ленивая итерация, экономит память
            if msg.role.code in (MessageRoleCodes.SYSTEM, MessageRoleCodes.AGENT):
                sender = FrontMessageRoleCodes.ASSISTANT
            else:
                sender = FrontMessageRoleCodes.CANDIDATE

            history.append(
                FrontDialogueMessage(
                    sender=sender,
                    content=msg.content,
                    created_at=msg.created_at.isoformat(),
                )
            )

        return history

    @staticmethod
    def get_message_dates(interview: Interview) -> MessageDates:
        """
        Возвращает даты самого первого и самого последнего сообщения в интервью
        в формате ISO 8601 строки (или None, если сообщений нет).

        Важно:
        - Если в интервью нет сообщений → оба значения будут None
        """
        # Один запрос, который вычисляет минимум и максимум по полю created_at
        agg_result = InterviewMessage.objects.filter(interview=interview).aggregate(
            first=Min("created_at"),
            last=Max("created_at"),
        )

        first_dt: Optional[datetime] = agg_result["first"]
        last_dt: Optional[datetime] = agg_result["last"]

        # Преобразуем datetime → ISO-строку только если значение существует
        first_iso = first_dt.isoformat() if first_dt else None
        last_iso = last_dt.isoformat() if last_dt else None

        return MessageDates(first=first_iso, last=last_iso)
