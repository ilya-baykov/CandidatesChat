from .validation_answer_ai import run_ai_validation_task
from .generate_questions_ai import generate_questions_for_interview


def start_generate_questions(interview_id: int, questions_count: int = 5) -> None:
    """Запускает задачу генерации вопросов."""
    generate_questions_for_interview.delay(
        interview_id=interview_id,
        questions_count=questions_count,
    )


def start_answer_validation(interview_id: int, question_id: int, answer_text: str) -> None:
    """Запускает задачу проверки ответа кандидата."""
    run_ai_validation_task.delay(
        interview_id=interview_id,
        question_id=question_id,
        answer_text=answer_text,
    )
