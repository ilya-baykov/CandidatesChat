import pytest
from apps.interviews.models import InterviewQuestion
from apps.interviews.services.ai_answer_validation.answer_validator import AIAnswerValidator
from core.ai_service.clients import gpt_4_model


@pytest.mark.slow
def test_real_ai_call():
    """
    Тест реального вызова ИИ.
    Используется для проверки промпта и результата от GPT-4.
    """
    question = InterviewQuestion(question_text="Расскажите о своем опыте с Python?")

    validator = AIAnswerValidator(client=gpt_4_model, max_attempts=1)

    result = validator.validate(
        question=question,
        answer_text="Я работал с Python 5 лет, создавал веб-приложения и API.",
        vacancy_title="Python Developer",
        vacancy_description="Разработка backend на Python, участие в проектах с Django и FastAPI",
        question_history=None
    )

    # Выводим результат для проверки
    print("Результат от ИИ:")
    print("is_correct:", result.is_correct)
    print("score:", result.score)
    print("reply_message:", result.reply_message)
    print("justification:", result.justification)

    # Проверка, что score корректный
    assert result.score >= 0
