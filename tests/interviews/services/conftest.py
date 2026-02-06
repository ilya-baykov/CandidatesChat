import pytest
from unittest.mock import Mock

from apps.interviews.services.answer_processing import InterviewAnswerProcessingService
from apps.interviews.collections import AnswerCodes


@pytest.fixture
def interview():
    interview = Mock()
    interview.pk = 1
    interview.candidate_id = 100
    return interview


@pytest.fixture
def question():
    question = Mock()
    question.pk = 10
    return question


@pytest.fixture
def vacancy():
    vacancy = Mock()
    vacancy.job_title = "Python Developer"
    vacancy.prompt_description = "Some description"
    return vacancy


@pytest.fixture
def service(interview, question, vacancy):
    service = InterviewAnswerProcessingService(
        interview=interview,
        question=question,
        vacancy=vacancy,
    )

    service.message_service = Mock()
    service.answer_service = Mock()
    service.question_service = Mock()
    service.interview_service = Mock()

    return service


@pytest.fixture
def validation_result():
    result = Mock()
    result.score = 50
    result.is_correct = True
    result.reply_message = None
    return result
