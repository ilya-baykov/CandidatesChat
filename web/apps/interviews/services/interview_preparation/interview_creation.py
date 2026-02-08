from django.db import transaction

from api.exceptions import InterviewAlreadyExists, CandidateNotFound, VacancyNotFound
from apps.reference.models import InterviewStatus
from core.integrations.oko.repositories.candidate_repository import OkoCandidateRepository
from core.integrations.oko.repositories.vacancy_repository import OkoVacancyRepository
from ...models import Interview
from ...collections import InterviewCodes
from ...tasks.triggers import start_generate_questions


class InterviewCreationService:
    """
    Use case: создание интервью.
    Инварианты:
      - кандидат должен существовать в ОКО
      - вакансия должна существовать в ОКО
      - интервью всегда создается вместе с запуском генерации вопросов
    """

    @staticmethod
    def execute(*, candidate_id: int, vacancy_id: int, questions_count: int = 5) -> tuple[Interview, bool]:

        # Проверяем внешние сущности (бизнес-инварианты)
        InterviewCreationService._validate_external_entities(candidate_id=candidate_id, vacancy_id=vacancy_id)

        with transaction.atomic():
            interview, created = Interview.objects.get_or_create(
                candidate_id=candidate_id,
                vacancy_id=vacancy_id,
                defaults={"status": InterviewStatus.objects.get(code=InterviewCodes.PENDING_QUESTIONS), },
            )

            # Если не создавали новое интервью
            if not created:
                raise InterviewAlreadyExists(interview)

            # Если создали — запускаем генерацию вопросов после коммита
            transaction.on_commit(
                lambda: start_generate_questions(
                    interview_id=interview.pk,
                    questions_count=questions_count,
                )
            )

        return interview, created

    @staticmethod
    def _validate_external_entities(*, candidate_id: int, vacancy_id: int) -> None:
        """
        Проверка обязательных внешних условий для создания интервью.
        """

        if not OkoCandidateRepository.candidate_exists(candidate_id):
            raise CandidateNotFound(candidate_id)

        if not OkoVacancyRepository.vacancy_exists(vacancy_id):
            raise VacancyNotFound(vacancy_id)
