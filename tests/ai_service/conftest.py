import pytest

from apps.interviews.models import InterviewQuestion


@pytest.fixture
def fake_question():
    return InterviewQuestion(question_text="Расскажите о своем опыте с Python?")