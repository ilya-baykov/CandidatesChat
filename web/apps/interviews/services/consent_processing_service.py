import logging

from apps.interviews.collections import AnswerCodes, InterviewCodes
from apps.interviews.models import Interview, InterviewQuestion
from apps.interviews.services.interviews import InterviewService
from apps.interviews.services.questions import QuestionService

logger = logging.getLogger(__name__)


class ConsentProcessingService:
    """Обработка ответа на вопрос о согласии."""

    def __init__(self, interview: Interview, question: InterviewQuestion):
        self.interview = interview
        self.question = question

    def process(self, answer_text: str) -> None:
        result = QuestionService.check_consent_answer(answer_text)

        if isinstance(result, bool):
            if result:
                logger.info(f"Интервью:{self.interview.pk} — согласие получено")
                QuestionService.mark_status(self.question, AnswerCodes.ANSWERED)

            else:
                logger.info(f"Интервью:{self.interview.pk} — кандидат отказался от обработки данных")
                QuestionService.mark_status(self.question, AnswerCodes.ANSWERED)
                InterviewService.set_status(self.interview, InterviewCodes.CONSENT_DECLINED)

        else:  # Если result - это None
            logger.info(f"Интервью:{self.interview.pk} — ответ на consent неясен, повторяем")
            QuestionService.mark_status(self.question, AnswerCodes.REPEAT)
