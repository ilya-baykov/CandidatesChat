from .answer_validation.dto import AnswerValidationResult
from .answer_validation.interfaces import AnswerValidator
from .answers import AnswerService
from .interviews import InterviewService
from .questions import QuestionService
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
        return QuestionService.get_current(self.interview)

    def submit_answer(self, *, question: InterviewQuestion, answer_text: str,
                      question_history: str | None = None) -> AnswerValidationResult:
        """
        1. Проверяет корректность через AnswerValidator
        2. Сохраняет ответ
        3. Применяет результат к flow
        4. Возвращает результат проверки (для UI)
        """

        # 1. Проверяем корректность ответа
        validation_result = self.answer_validator.validate(
            vacancy_title=self.interview.vacancy.title,
            vacancy_description=self.interview.vacancy.vacancy_description,
            question=question,
            answer_text=answer_text,
            question_history=question_history,
        )

        # 2. Сохраняем ответ кандидата
        AnswerService.save(question=question, answer_text=answer_text, score=validation_result.score)

        # 3. Управляем flow
        if validation_result.is_correct:
            QuestionService.mark_answered(question)
        else:
            QuestionService.mark_repeat(question)

        # 4. Проверяем завершение интервью
        InterviewService.complete_if_done(self.interview)

        return validation_result
