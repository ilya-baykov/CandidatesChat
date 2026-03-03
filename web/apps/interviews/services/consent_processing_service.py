import logging

from apps.interviews.collections import AnswerCodes, InterviewCodes, MessageRoleCodes
from apps.interviews.models import Interview, InterviewQuestion
from apps.interviews.services.answers import AnswerService
from apps.interviews.services.constants import CONSENT_REPEAT_MESSAGE, CONSENT_DECLINE_MESSAGE
from apps.interviews.services.interviews import InterviewService
from apps.interviews.services.message_service import MessageService
from apps.interviews.services.questions import QuestionService
from core.integrations.oko.services.candidate_status_service import OkoCandidateStatusService

logger = logging.getLogger(__name__)


class ConsentProcessingService:
    """
    Use-case обработки ответа кандидата на вопрос о согласии на обработку данных.

    Flow обработки:
    1. Валидация ответа кандидата
    2. Сохранение ответа
    3. Формирование ответного сообщения (если требуется)
    4. Обновление статуса вопроса
    5. Обновление статуса интервью при отказе

    Архитектурно сервис повторяет структуру AI-обработки ( InterviewAnswerProcessingService  ),
    чтобы поддерживать единый conversational flow.
    """

    MAX_ATTEMPTS = 5

    answer_service = AnswerService
    message_service = MessageService
    question_service = QuestionService
    interview_service = InterviewService

    def __init__(self, interview: Interview, question: InterviewQuestion):
        self.interview = interview
        self.question = question

    def process(self, answer_text: str) -> None:
        """
        Основной сценарий обработки ответа кандидата.

        Последовательность выполнения соответствует AI-процессору:
        validation -> save -> reply -> status update -> side effects
        """
        # Проверка ответа
        validation = self._validate(answer_text)

        # Сохраняем ответ кандидата (важно для анализа и attempt_count)
        answer = self.answer_service.save(question=self.question, answer_text=answer_text, score=validation["score"])

        # Сохранение "Ответного" сообщения для пользователя
        self._handle_reply(answer, validation)

        # Обновление статуса вопроса
        self._update_question_status(answer, validation)

        # Проверка отказа от собеседования
        self._handle_decline(validation)

        # Проверка лимитов
        self._handle_attempt_limit(answer, validation)

        logger.info(f"Интервью:{self.interview.pk} — consent обработан.")

    def _validate(self, answer_text: str) -> dict:
        result = self.question_service.check_consent_answer(answer_text)

        if isinstance(result, bool):
            return {
                "is_correct": True,
                "score": 100 if result else 0,
                "reply_message": None,
                "is_declined": result is False,
            }

        return {
            "is_correct": False,
            "score": 0,
            "reply_message": CONSENT_REPEAT_MESSAGE,
            "is_declined": False,
        }

    def _handle_reply(self, answer, validation: dict) -> None:
        if validation["reply_message"] and answer.attempt_count < self.MAX_ATTEMPTS:
            self.message_service.add_message(
                interview=self.interview,
                question=self.question,
                role_code=MessageRoleCodes.AGENT,
                content=validation["reply_message"],
            )

    def _update_question_status(self, answer, validation: dict) -> None:
        next_status = (
            AnswerCodes.ANSWERED
            if validation["is_correct"]
               or answer.attempt_count >= self.MAX_ATTEMPTS
            else AnswerCodes.REPEAT
        )

        self.question_service.mark_status(
            question=self.question,
            code=next_status,
        )

    def _handle_decline(self, validation: dict) -> None:
        if validation["is_declined"]:
            logger.info(f"Интервью:{self.interview.pk} — кандидат отказался от обработки данных")
            self.interview_service.set_status(self.interview, InterviewCodes.CONSENT_DECLINED)

            # Обновляем статус кандидата
            OkoCandidateStatusService.mark_interview_refusal(candidate_id=self.interview.candidate_id)

    def _handle_attempt_limit(self, answer, validation: dict) -> None:
        """
        Неявный отказ — исчерпание попыток.
        """

        if not validation["is_correct"] and (answer.attempt_count + 1) >= self.MAX_ATTEMPTS:
            logger.info(f"Интервью:{self.interview.pk} — исчерпаны попытки согласия")

            # Optional: отдельный message
            self.message_service.add_message(
                interview=self.interview,
                question=self.question,
                role_code=MessageRoleCodes.AGENT,
                content=CONSENT_DECLINE_MESSAGE,
            )

            self.interview_service.set_status(self.interview, InterviewCodes.CONSENT_DECLINED)
            OkoCandidateStatusService.mark_interview_refusal(candidate_id=self.interview.candidate_id)
