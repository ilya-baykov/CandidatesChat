from ..models import Interview, InterviewMessage, InterviewQuestion
from ...reference.models import MessageRole


class MessageService:
    @staticmethod
    def add_message(*, interview: Interview, role_code: str, content: str,
                    question: InterviewQuestion | None = None) -> InterviewMessage:
        """Добавление сообщения в лог/истории чата"""
        role = MessageRole.objects.get(code=role_code)

        message_obj = InterviewMessage.objects.create(interview=interview, question=question,
                                                      role=role, content=content)
        return message_obj

    @staticmethod
    def build_question_history(*, interview: Interview, question: InterviewQuestion) -> str:
        """
        Формирует историю диалога по конкретному вопросу
        для передачи в ИИ.
        """

        messages = (
            InterviewMessage.objects
            .filter(interview=interview, question=question)
            .select_related("role")
            .order_by("created_at")
        )

        history_lines: list[str] = []

        for msg in messages:
            history_lines.append(
                f"{msg.role.code.upper()}: {msg.content}"
            )

        return "\n".join(history_lines)

    @staticmethod
    def ensure_system_question_logged(*, interview: Interview, question: InterviewQuestion) -> None:
        """
        Гарантирует, что system-сообщение с текстом вопроса
        записано в историю интервью (идемпотентно).
        """

        exists = InterviewMessage.objects.filter(
            interview=interview,
            question=question,
            role__code="system",
            content=question.question_text,
        ).exists()

        if not exists:
            MessageService.add_message(
                interview=interview,
                question=question,
                role_code="system",
                content=question.question_text,
            )
