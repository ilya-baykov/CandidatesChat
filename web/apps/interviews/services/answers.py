from django.utils import timezone

from ..models import InterviewQuestion, InterviewAnswer


class AnswerService:
    """Сервис для работы с ответами кандидата."""

    @staticmethod
    def save(*, question: InterviewQuestion, answer_text: str, score: float | None = None) -> InterviewAnswer:
        """Сохраняет или обновляет ответ на вопрос."""
        answer, created = InterviewAnswer.objects.get_or_create(
            interview_question=question,
            defaults={
                "answer_text": answer_text,
                "score": score,
                "answered_at": timezone.now(),
            },
        )

        if not created:
            answer.answer_text = answer_text
            answer.score = score
            answer.answered_at = timezone.now()
            answer.save(update_fields=["answer_text", "score", "answered_at"])

        return answer
