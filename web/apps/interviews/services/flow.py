from . import QuestionService, AnswerService, InterviewService
from ..models import Interview, InterviewQuestion


class InterviewFlowService:
    """
    Оркестратор flow интервью:
    - Сохраняет ответы кандидата
    - Меняет статус вопросов (answered/repeat)
    - Завершает интервью при необходимости
    """

    def __init__(self, interview: Interview):
        self.interview = interview

    def get_current_question(self) -> InterviewQuestion | None:
        """Возвращает текущий вопрос для отображения кандидату."""
        return QuestionService.get_current(self.interview)

    def submit_answer(self, *, question: InterviewQuestion, answer_text: str,
                      is_correct: bool) -> InterviewQuestion | None:
        """
        Сохраняет ответ и управляет статусом вопроса.
        """
        AnswerService.save(question=question, answer_text=answer_text)

        if is_correct:
            QuestionService.mark_answered(question)
        else:
            QuestionService.mark_repeat(question)

        InterviewService.complete_if_done(self.interview)

        return self.get_current_question()
