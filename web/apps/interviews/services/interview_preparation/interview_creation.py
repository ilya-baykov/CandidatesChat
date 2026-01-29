from django.db import transaction

from api.exceptions import InterviewAlreadyExists
from apps.reference.models import InterviewStatus
from ...models import Interview
from ...collections import InterviewCodes
from ...tasks.triggers import start_generate_questions


class InterviewCreationService:
    """
    Use case: создание интервью.
    Инвариант:
      - интервью всегда создается вместе с запуском генерации вопросов
    """

    @staticmethod
    def execute(*, candidate_id: int, vacancy_id: int, questions_count: int = 5) -> tuple[Interview, bool]:
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
            if created:
                transaction.on_commit(
                    lambda: start_generate_questions(
                        interview_id=interview.pk,
                        questions_count=questions_count,
                    )
                )

        return interview, created
