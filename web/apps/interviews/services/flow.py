from .ai_answer_validation.answer_validator import AnswerValidator, AIAnswerValidator, ai_answer_validator
from .ai_answer_validation.dto import AnswerValidationResult
from .answers import AnswerService
from .constants import INTERVIEW_SAVED_MESSAGE
from .interviews import InterviewService
from .message_service import MessageService
from .questions import QuestionService
from ..collections import AnswerCodes
from ..models import Interview, InterviewQuestion


class InterviewFlowService:
    """
    Оркестратор flow интервью:
    - Сохраняет ответы кандидата
    - Меняет статус вопросов (answered/repeat)
    - Завершает интервью при необходимости
    """

    AI_ANSWER_VALIDATOR = ai_answer_validator

    def __init__(self, interview: Interview):
        self.interview = interview

    def get_current_question(self) -> InterviewQuestion | None:
        """Возвращает текущий вопрос для отображения кандидату."""
        question = QuestionService.get_current(self.interview)
        return question

    def submit_answer(self, *, question: InterviewQuestion, answer_text: str) -> AnswerValidationResult:
        # Принимаем ответ от пользователя
        self._accept_answer(question=question, answer_text=answer_text)

        # Формируем историю вопроса
        history = MessageService.build_question_history(interview=self.interview, question=question)
        result = self._run_ai_validation(question=question, answer_text=answer_text, question_history=history)

        # Применяем результат валидации
        self._apply_validation_result(question=question, answer_text=answer_text, validation_result=result)

        # Проверяем завершенность интервью
        self._advance_interview_if_needed()

        return result

    def _accept_answer(self, *, question: InterviewQuestion, answer_text: str) -> None:
        """
        Быстрый синхронный шаг:
        - сохраняем ответ кандидата
        - помечаем вопрос как 'validating'
        """

        MessageService.add_message(
            interview=self.interview,
            question=question,
            role_code="candidate",
            content=answer_text,
        )

        QuestionService.mark_status(
            question=question,
            code=AnswerCodes.VALIDATING,
        )

    def _run_ai_validation(self, *, question: InterviewQuestion, answer_text: str,
                          question_history: str) -> AnswerValidationResult:
        validate_result = self.AI_ANSWER_VALIDATOR.validate(
            vacancy_title=self.interview.vacancy.title,
            vacancy_description=self.interview.vacancy.vacancy_description,
            question=question,
            answer_text=answer_text,
            question_history=question_history,
        )

        return validate_result

    def _apply_validation_result(self, *, question: InterviewQuestion, answer_text: str,
                                validation_result: AnswerValidationResult) -> None:
        if validation_result.reply_message:
            MessageService.add_message(
                interview=self.interview,
                question=question,
                role_code="agent",
                content=validation_result.reply_message,
            )

        AnswerService.save(
            question=question,
            answer_text=answer_text,
            score=validation_result.score,
        )

        next_status = (
            AnswerCodes.SCORED
            if validation_result.is_correct
            else AnswerCodes.REPEAT
        )

        QuestionService.mark_status(question, next_status)

    def _advance_interview_if_needed(self) -> None:
        interview_completed = InterviewService.complete_if_done(self.interview)

        if interview_completed:
            MessageService.add_message(
                interview=self.interview,
                role_code="system",
                content=INTERVIEW_SAVED_MESSAGE,
            )

