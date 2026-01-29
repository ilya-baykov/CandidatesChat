import logging

from .ai_answer_validation.answer_validator import ai_answer_validator
from .answers import AnswerService
from .constants import INTERVIEW_SAVED_MESSAGE
from .interview_preparation.dto import VacancyContextDTO
from .interviews import InterviewService
from .message_service import MessageService
from .questions import QuestionService
from ..collections import AnswerCodes, MessageRoleCodes
from ..models import Interview, InterviewQuestion

logger = logging.getLogger(__name__)


class InterviewAnswerProcessingService:
    """
    Асинхронный use-case обработки ответа кандидата.

    Запускается:
    - через Celery
    """
    AI_ANSWER_VALIDATOR = ai_answer_validator

    message_service = MessageService
    question_service = QuestionService
    answer_service = AnswerService
    interview_service = InterviewService

    def __init__(self, interview: Interview, question: InterviewQuestion, vacancy: VacancyContextDTO):
        """
        Инициализация
        :param interview: Текущее интервью
        :param question:  Текущий вопрос
        :param vacancy:   Текущая вакансия (связана с интервью)
        """
        self.interview = interview
        self.question = question
        self.vacancy = vacancy

    def process(self, *, answer_text: str) -> None:
        """
        Полный use-case обработки ответа:
        - формирование истории
        - AI-валидация
        - применение результата
        - завершение интервью
        """
        logger.info(f"Обработка ответа кандидата для Интервью:{self.interview.pk}, Вопрос:{self.question.pk}")

        # История вопроса
        history = self.message_service.build_question_history(interview=self.interview, question=self.question)

        # Валидация ответа (долгая операция)
        validation_result = self.AI_ANSWER_VALIDATOR.validate(
            vacancy_title=self.vacancy.job_title,
            vacancy_description=self.vacancy.prompt_description,
            question=self.question,
            answer_text=answer_text,
            question_history=history)
        logger.info(f"Результат AI-валидации для Интервью:{self.interview.pk}, Вопрос:{self.question.pk} "
                    f"Score:{validation_result.score}, Correct:{validation_result.is_correct}")

        # Применение результата валидации
        self._apply_validation_result(answer_text=answer_text, validation_result=validation_result)

        # Завершение интервью при необходимости *
        self._advance_interview_if_needed()

    def _apply_validation_result(self, *, answer_text: str, validation_result) -> None:
        """Применяет результат AI-валидации."""
        if validation_result.reply_message:
            self.message_service.add_message(
                interview=self.interview,
                question=self.question,
                role_code=MessageRoleCodes.AGENT,
                content=validation_result.reply_message)
            logger.debug(f"Отправлено сообщение от агента для Интервью:{self.interview.pk}, Вопрос:{self.question.pk}")

        self.answer_service.save(
            question=self.question,
            answer_text=answer_text,
            score=validation_result.score)

        next_status = (
            AnswerCodes.SCORED
            if validation_result.is_correct
            else AnswerCodes.REPEAT
        )
        
        self.question_service.mark_status(question=self.question, code=next_status)
        logger.info(f"Статус вопроса обновлен для Интервью:{self.interview.pk}, Вопрос:{self.question.pk} "
                    f"Новый статус:{next_status}")

    def _advance_interview_if_needed(self) -> None:
        """Завершает интервью, если активных вопросов больше нет."""
        completed = self.interview_service.complete_if_done(self.interview)

        if completed:
            self.message_service.add_message(
                interview=self.interview,
                role_code=MessageRoleCodes.SYSTEM,
                content=INTERVIEW_SAVED_MESSAGE,
            )
