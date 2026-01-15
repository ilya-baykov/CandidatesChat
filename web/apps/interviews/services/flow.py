from .ai_answer_validation.answer_validator import ai_answer_validator
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
    Оркестратор flow интервью (Application Layer):

    Отвечает за:
    - приём и обработку ответов кандидата
    - запуск AI-валидации
    - изменение статусов вопросов
    - логирование сообщений (candidate / agent / system)
    - завершение интервью
    - формирование UI-ready состояния
    """

    # Конфигурационные зависимости (можно подменять)
    AI_ANSWER_VALIDATOR = ai_answer_validator

    # Рабочие сервисы (dependencies)
    message_service = MessageService
    question_service = QuestionService
    answer_service = AnswerService
    interview_service = InterviewService

    def __init__(self, interview: Interview):
        self.interview = interview

    def get_state_for_display(self) -> dict:
        """
        Возвращает состояние интервью, готовое для отображения в UI:
        - текущий вопрос
        - сообщения
        Гарантирует, что system-вопрос залогирован ровно один раз.
        """
        question = self.question_service.get_current(self.interview)

        if question:
            self.message_service.ensure_system_question_logged(interview=self.interview, question=question)

        messages = self.interview.messages.select_related("role").order_by("created_at")  # noqa
        contex = {"current_question": question, "messages": messages}
        return contex

    def submit_answer(self, *, question: InterviewQuestion, answer_text: str) -> AnswerValidationResult:
        """
        Основной use-case:
        - принимает ответ кандидата
        - запускает AI-валидацию
        - применяет результат
        - при необходимости завершает интервью
        """

        # 1. Принимаем ответ (быстро и синхронно)
        self._accept_answer(question=question, answer_text=answer_text)

        # 2. Формируем историю вопроса
        history = self.message_service.build_question_history(interview=self.interview, question=question)

        # 3. Запускаем AI-валидацию
        validation_result = self._run_ai_validation(question=question, answer_text=answer_text,
                                                    question_history=history)

        # 4. Применяем результат
        self._apply_validation_result(question=question, answer_text=answer_text, validation_result=validation_result)

        # 5. Проверяем завершение интервью
        self._advance_interview_if_needed()

        return validation_result

    def _accept_answer(self, *, question: InterviewQuestion, answer_text: str) -> None:
        """
        Синхронный шаг:
        - сохраняем сообщение кандидата
        - помечаем вопрос как validating
        """
        self.message_service.add_message(interview=self.interview, question=question,
                                         role_code="candidate", content=answer_text, )

        self.question_service.mark_status(question=question, code=AnswerCodes.VALIDATING)

    def _run_ai_validation(self, *, question: InterviewQuestion, answer_text: str,
                           question_history: str) -> AnswerValidationResult:
        """
        Запуск AI-валидации ответа.
        """
        validation_result = self.AI_ANSWER_VALIDATOR.validate(
            vacancy_title=self.interview.vacancy.title,
            vacancy_description=self.interview.vacancy.vacancy_description,
            question=question,
            answer_text=answer_text,
            question_history=question_history,
        )
        return validation_result

    def _apply_validation_result(self, *, question: InterviewQuestion, answer_text: str,
                                 validation_result: AnswerValidationResult) -> None:
        """
        Применяет результат AI-валидации:
        - сообщение агента (если есть)
        - сохранение ответа
        - смена статуса вопроса
        """
        if validation_result.reply_message:
            self.message_service.add_message(
                interview=self.interview,
                question=question,
                role_code="agent",
                content=validation_result.reply_message,
            )

        self.answer_service.save(question=question, answer_text=answer_text, score=validation_result.score)

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
        Завершает интервью, если больше нет активных вопросов.
        """
        interview_completed = self.interview_service.complete_if_done(self.interview)

        if interview_completed:
            self.message_service.add_message(
                interview=self.interview,
                role_code="system",
                content=INTERVIEW_SAVED_MESSAGE,
            )
