from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView

from apps.interviews.models import Interview


class InterviewAlreadyExists(Exception):
    def __init__(self, interview: Interview):
        self.interview = interview


class CandidateNotFound(Exception):
    """Канидат не найден в БД"""

    def __init__(self, candidate_id: int):
        self.candidate_id = candidate_id


class VacancyNotFound(Exception):
    """Вакансия не найдена в БД"""

    def __init__(self, vacancy_id: int):
        self.vacancy_id = vacancy_id


class InterviewAlreadyExistsAPIException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "interview_already_exists"

    def __init__(self, interview: Interview):
        self.detail = {
            "detail": "Интервью уже существует",
            "interview_id": interview.pk,
            "token": str(interview.token),
        }


class CandidateNotFoundAPIException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "candidate_not_found"

    def __init__(self, candidate_id: int):
        self.detail = {
            "detail": f"Кандидат с id={candidate_id} не найден",
            "candidate_id": candidate_id,
        }


class VacancyNotFoundAPIException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "vacancy_not_found"

    def __init__(self, vacancy_id: int):
        self.detail = {
            "detail": f"Вакансия с id={vacancy_id} не найдена",
            "vacancy_id": vacancy_id,
        }
