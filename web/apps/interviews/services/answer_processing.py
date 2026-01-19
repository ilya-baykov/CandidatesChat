from .ai_answer_validation.answer_validator import ai_answer_validator
from .answers import AnswerService
from .constants import INTERVIEW_SAVED_MESSAGE
from .interviews import InterviewService
from .message_service import MessageService
from .questions import QuestionService
from ..collections import AnswerCodes
from ..models import Interview, InterviewQuestion


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

    def __init__(self, interview: Interview):
        self.interview = interview

    def process(self, *, question: InterviewQuestion, answer_text: str) -> None:
        """
        Полный use-case обработки ответа:
        - формирование истории
        - AI-валидация
        - применение результата
        - завершение интервью
        """
        history = self.message_service.build_question_history(
            interview=self.interview,
            question=question,
        )

        validation_result = self.AI_ANSWER_VALIDATOR.validate(
            vacancy_title=self.interview.vacancy.title,
            vacancy_description=self.interview.vacancy.vacancy_description,
            question=question,
            answer_text=answer_text,
            question_history=history,
        )
        print(validation_result)
        self._apply_validation_result(
            question=question,
            answer_text=answer_text,
            validation_result=validation_result,
        )

        self._advance_interview_if_needed()

    # ------------------------------------------------------------------
    # Internal steps
    # ------------------------------------------------------------------

    def _apply_validation_result(
            self,
            *,
            question: InterviewQuestion,
            answer_text: str,
            validation_result,
    ) -> None:
        """
        Применяет результат AI-валидации.
        """
        if validation_result.reply_message:
            self.message_service.add_message(
                interview=self.interview,
                question=question,
                role_code="agent",
                content=validation_result.reply_message,
            )

        self.answer_service.save(
            question=question,
            answer_text=answer_text,
            score=validation_result.score,
        )

        next_status = (
            AnswerCodes.SCORED
            if validation_result.is_correct
            else AnswerCodes.REPEAT
        )

        self.question_service.mark_status(
            question=question,
            code=next_status,
        )

    def _advance_interview_if_needed(self) -> None:
        """
        Завершает интервью, если активных вопросов больше нет.
        """
        completed = self.interview_service.complete_if_done(self.interview)

        if completed:
            self.message_service.add_message(
                interview=self.interview,
                role_code="system",
                content=INTERVIEW_SAVED_MESSAGE,
            )
