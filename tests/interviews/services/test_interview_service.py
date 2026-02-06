from unittest.mock import Mock
from apps.interviews.services.interviews import InterviewService

def test_calculate_total_score_returns_average_from_orm(mocker):
    """
    Возвращается средний score, если ORM вернул значение.
    """

    interview = Mock()

    # Мокаем цепочку:
    # InterviewAnswer.objects.filter(...).aggregate(...)
    answers_qs = Mock()
    answers_qs.aggregate.return_value = {"avg_score": 0.75}

    filter_mock = mocker.patch(
        "apps.interviews.services.interviews.InterviewAnswer.objects.filter",
        return_value=answers_qs,
    )

    result = InterviewService._calculate_total_score(interview)

    filter_mock.assert_called_once_with(
        interview_question__interview=interview,
        score__isnull=False,
    )
    answers_qs.aggregate.assert_called_once()

    assert result == 0.75


def test_calculate_total_score_returns_zero_if_avg_is_none(mocker):
    """
    Если ORM вернул None — метод возвращает 0.0.
    """

    interview = Mock()

    answers_qs = Mock()
    answers_qs.aggregate.return_value = {"avg_score": None}

    mocker.patch(
        "apps.interviews.services.interviews.InterviewAnswer.objects.filter",
        return_value=answers_qs,
    )

    result = InterviewService._calculate_total_score(interview)

    assert result == 0.0
