from unittest.mock import Mock

from apps.interviews.services.ai_question_generation.dto import GeneratedQuestion
from apps.interviews.services.ai_question_generation.generator import AIQuestionGenerator


def test_generate_questions_success_from_ai(mocker):
    """
    AI возвращает валидный JSON со списком вопросов.
    Генератор должен вернуть список GeneratedQuestion.
    """

    mock_client = Mock()
    mock_client.get_answer.return_value = """
    {
        "questions": [
            {"order": 1, "text": "Что такое GIL в Python?"},
            {"order": 2, "text": "Опыт работы с Django?"}
        ]
    }
    """

    generator = AIQuestionGenerator(client=mock_client, max_attempts=1)

    result = generator.generate(
        vacancy_title="Python Developer",
        vacancy_description="Backend dev",
        candidate_resume="5 years Python",
        questions_count=2,
    )

    assert len(result) == 2
    assert isinstance(result[0], GeneratedQuestion)
    assert result[0].order == 1
    assert result[0].text == "Что такое GIL в Python?"
    assert mock_client.get_answer.called


def test_generate_questions_retries_if_ai_returns_empty_json():
    """
    Если AI вернул мусор, генератор должен сделать retry.
    """

    mock_client = Mock()
    mock_client.get_answer.side_effect = [
        "bla bla",  # не JSON
        '{"questions": [{"order": 1, "text": "Опыт с FastAPI?"}]}',
    ]

    generator = AIQuestionGenerator(client=mock_client, max_attempts=2)

    result = generator.generate(
        vacancy_title="Python Dev",
        vacancy_description="Backend",
        candidate_resume="CV",
        questions_count=1,
    )

    assert len(result) == 1
    assert mock_client.get_answer.call_count == 2


def test_generate_questions_invalid_questions_format_returns_empty():
    """
    Если AI вернул questions не списком — результат пустой.
    """

    mock_client = Mock()
    mock_client.get_answer.return_value = '{"questions": "not-a-list"}'

    generator = AIQuestionGenerator(client=mock_client, max_attempts=1)

    result = generator.generate(
        vacancy_title="Python Dev",
        vacancy_description="Backend",
        candidate_resume="CV",
        questions_count=1,
    )

    assert result == []


def test_generate_questions_skips_invalid_items():
    """
    Некорректные элементы списка questions игнорируются.
    """

    mock_client = Mock()
    mock_client.get_answer.return_value = """
    {
        "questions": [
            {"order": 1, "text": "Валидный вопрос"},
            {"order": "bad", "text": "Некорректный order"},
            {"text": "Нет order"}
        ]
    }
    """

    generator = AIQuestionGenerator(client=mock_client, max_attempts=1)

    result = generator.generate(
        vacancy_title="Python Dev",
        vacancy_description="Backend",
        candidate_resume="CV",
        questions_count=3,
    )

    assert len(result) == 1
    assert result[0].text == "Валидный вопрос"


def test_generate_questions_returns_empty_after_max_attempts():
    """
    После max_attempts неудачных попыток возвращается пустой список.
    """

    mock_client = Mock()
    mock_client.get_answer.return_value = "invalid response"

    generator = AIQuestionGenerator(client=mock_client, max_attempts=3)

    result = generator.generate(
        vacancy_title="Python Dev",
        vacancy_description="Backend",
        candidate_resume="CV",
        questions_count=3,
    )

    assert result == []
    assert mock_client.get_answer.call_count == 3
