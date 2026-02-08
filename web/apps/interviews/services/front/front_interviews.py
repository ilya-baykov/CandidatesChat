import logging
from typing import Optional

from django.db.models import Min, Max
from datetime import datetime
from ...collections import MessageRoleCodes, FrontDialogueMessage, FrontMessageRoleCodes, MessageDates
from ...models import Interview, InterviewMessage

logger = logging.getLogger(__name__)


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

        message_count = messages.count()
        logger.debug("Найдено сообщений: %d для interview_id=%s", message_count, interview.pk)

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
        if logger.isEnabledFor(logging.DEBUG) and len(history) > 0:
            logger.debug("Дата первого сообщения: %s | Последнего: %s",
                         history[0].get('created_at'), history[-1].get('created_at'))
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

        if first_dt is None and last_dt is None:
            logger.debug("Сообщений не найдено для interview_id=%s", interview.pk)
        else:
            logger.debug("Диапазон дат: first=%s → last=%s (interview_id=%s)",
                         first_dt.isoformat(), last_dt.isoformat(), interview.pk)

        # Преобразуем datetime → ISO-строку только если значение существует
        first_iso = first_dt.isoformat() if first_dt else None
        last_iso = last_dt.isoformat() if last_dt else None

        return MessageDates(first=first_iso, last=last_iso)
