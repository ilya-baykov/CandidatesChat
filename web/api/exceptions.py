from rest_framework import status
from rest_framework.exceptions import APIException

from apps.interviews.models import Interview


class InterviewAlreadyExists(Exception):
    def __init__(self, interview: Interview):
        self.interview = interview


class InterviewAlreadyExistsAPIException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "interview_already_exists"

    def __init__(self, interview: Interview):
        self.detail = {
            "detail": "Интервью уже существует",
            "interview_id": interview.pk,
            "token": str(interview.token),
        }