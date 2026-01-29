from .message_service import MessageService
from .questions import QuestionService
from ..collections import AnswerCodes, MessageRoleCodes
from ..models import Interview, InterviewQuestion


class InterviewFlowService:
    """
    Sync-оркестратор flow интервью (Application Layer).

    Отвечает за:
    - приём ответа кандидата
    - быстрые синхронные операции
    - подготовку состояния для UI
    """

    message_service = MessageService
    question_service = QuestionService

    def __init__(self, interview: Interview):
        self.interview = interview

    def get_state_for_display(self) -> dict:
        """
        Возвращает состояние интервью, готовое для отображения в UI.
        """
        question = self.question_service.get_current(self.interview)

        if question:
            self.message_service.ensure_system_question_logged(
                interview=self.interview,
                question=question,
            )

        messages = (
            self.interview.messages  # noqa
            .select_related("role")
            .order_by("created_at")
        )

        context = {
            "current_question": question,
            "messages": messages,
            "is_processing": question and question.status.code == AnswerCodes.VALIDATING.value,
            "needs_repeat": question and question.status.code == AnswerCodes.REPEAT.value,
        }
        print("get_state_for_display: ", context)
        return context

    def submit_answer(self, *, question: InterviewQuestion, answer_text: str) -> None:
        """
        Синхронный entry-point.

        Делает только то, что должно быть быстрым:
        - сохраняет сообщение кандидата
        - помечает вопрос как VALIDATING
        """

        self.message_service.add_message(
            interview=self.interview,
            question=question,
            role_code=MessageRoleCodes.CANDIDATE,
            content=answer_text,
        )

        self.question_service.mark_status(
            question=question,
            code=AnswerCodes.VALIDATING,
        )
