from .answer_validation.dto import AnswerValidationResult
from .answer_validation.interfaces import AnswerValidator
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

    def __init__(self, interview: Interview, answer_validator: AnswerValidator):
        self.interview = interview
        self.answer_validator = answer_validator

    def get_current_question(self) -> InterviewQuestion | None:
        """Возвращает текущий вопрос для отображения кандидату."""
        question = QuestionService.get_current(self.interview)
        return question

    def submit_answer(self, *, question: InterviewQuestion, answer_text: str) -> AnswerValidationResult:
        """
        1. Сохраняет сообщение кандитата (для истории чата)
        2. Проверят корректность ответа пользователя
        3. Сохраняет сообщение ИИ-агента (для истории чата)
        4. Сохраняет состояние ответа
        5. Возвращает результат проверки (для UI)
        """

        # 1 Сообщение кандидата
        MessageService.add_message(
            interview=self.interview,
            question=question,
            role_code="candidate",
            content=answer_text,
        )
        # Обновляем статус вопроса (получен ответ, но пока не оценен)
        QuestionService.mark_status(question=question, code=AnswerCodes.ANSWERED)

        # Формируем историю диалога
        question_history = MessageService.build_question_history(interview=self.interview, question=question)

        # 2 Валидация
        validation_result = self.answer_validator.validate(
            vacancy_title=self.interview.vacancy.title,
            vacancy_description=self.interview.vacancy.vacancy_description,
            question=question,
            answer_text=answer_text,
            question_history=question_history,
        )

        # 3 Сообщение ИИ (если оно не пустое)
        if validation_result.reply_message:
            MessageService.add_message(
                interview=self.interview,
                question=question,
                role_code="agent",
                content=validation_result.reply_message,
            )

        # 4 Агрегированное состояние ответа
        AnswerService.save(
            question=question,
            answer_text=answer_text,
            score=validation_result.score,
        )

        # 5 Flow
        if validation_result.is_correct:
            QuestionService.mark_status(question=question, code=AnswerCodes.SCORED)
        else:
            QuestionService.mark_status(question=question, code=AnswerCodes.REPEAT)

        # Проверяем завершение интервью
        interview_completed = InterviewService.complete_if_done(self.interview)

        if interview_completed:
            MessageService.add_message(
                interview=self.interview,
                role_code="system",
                content=INTERVIEW_SAVED_MESSAGE
            )

        return validation_result
