from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.exceptions import InterviewNotFoundAPIException
from apps.interviews.services.interviews import InterviewService
from api.views.interviews.validators import Validator
from apps.interviews.models import Interview
from api.serializers.interviews import InterviewDetailSerializer


class InterviewByTokenMixin:
    @staticmethod
    def get_interview_by_token(token: str) -> Interview:
        uuid_obj = Validator.validate_uuid(token)
        return get_object_or_404(Interview, token=uuid_obj)


class InterviewByCandidateVacancyMixin:

    @staticmethod
    def get_interview_by_candidate_vacancy(candidate_id: int, vacancy_id: int) -> Interview:
        try:
            return InterviewService.get_by_candidate_and_vacancy(candidate_id=candidate_id, vacancy_id=vacancy_id)
        except Interview.DoesNotExist:
            raise InterviewNotFoundAPIException(candidate_id=candidate_id, vacancy_id=vacancy_id)
