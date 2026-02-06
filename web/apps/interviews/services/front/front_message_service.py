from .front_interviews import FrontMessageService
from ...models import Interview
from ...collections import InterviewCodes, MessageDates, FrontDialogueMessage, FrontInterviewSummary


class FrontInterviewService:
    """
    Сервис, который готовит данные об интервью в формате,
    максимально удобном для фронтенд-приложения.

    Не содержит бизнес-логики — только агрегацию и форматирование.
    """

    @staticmethod
    def get_summary(interview: Interview) -> FrontInterviewSummary:
        """
        Возвращает полную сводку по интервью для фронтенда.

        Основные поля:
        - candidate_id
        - vacancy_id
        - current_status         (строковый код статуса)
        - first_message_date     (ISO или null)
        - last_message_date      (ISO или null)
        - total_score            (число или null)
        - dialogue_history       (список сообщений в нужном формате)
        - is_completed           (удобный флаг для фронта)

        Примечание: предполагается, что interview передан с prefetch_related,
        если вы хотите минимизировать количество запросов.
        """
        # Получаем даты сообщений одним запросом
        dates: MessageDates = FrontMessageService.get_message_dates(interview)

        # Получаем историю диалога
        history: list[FrontDialogueMessage] = FrontMessageService.get_dialogue_history(interview)

        # Дополнительные вычисляемые поля (удобно для фронта)
        is_completed = interview.status.code == InterviewCodes.COMPLETED
        is_in_progress = interview.status.code == InterviewCodes.IN_PROGRESS

        interview_summary: FrontInterviewSummary = {
            "candidate_id": interview.candidate_id,
            "vacancy_id": interview.vacancy_id,
            "current_status": interview.status.code,
            "first_message_date": dates.first,
            "last_message_date": dates.last,
            "total_score": interview.total_score,
            "started_at": interview.started_at.isoformat() if interview.started_at else None,
            "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
            "is_completed": is_completed,
            "is_in_progress": is_in_progress,
            "dialogue_history": history,
        }

        return interview_summary
