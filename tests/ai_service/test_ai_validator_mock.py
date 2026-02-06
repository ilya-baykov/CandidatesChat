from unittest.mock import Mock
from apps.interviews.services.ai_answer_validation.answer_validator import AIAnswerValidator


def test_ai_validator_mock(fake_question):
    """
    Быстрый мок-тест для экспериментов с промптом
    """
    mock_client = Mock()
    mock_client.get_answer.return_value = '{"score": 5, "is_correct": true, "reply_message": "Отлично", "justification": "Хорошо"}'

    validator = AIAnswerValidator(client=mock_client, max_attempts=1)

    result = validator.validate(
        question=fake_question,
        answer_text="Я пишу на Python 5 лет",
        vacancy_title="Python Developer",
        vacancy_description="Разработка backend на Python"
    )

    # Проверяем, что мок вызвался
    assert mock_client.get_answer.called
    assert result.score == 5
    assert result.is_correct is True
