import logging

from apps.exceptions import InterviewGenerationError
from apps.interviews.models import InterviewQuestion
from apps.interviews.services.ai_question_generation.generator import QuestionGenerator
from apps.interviews.services.interview_preparation.dto import CandidateContextDTO, VacancyContextDTO
from apps.reference.models import AnswerStatus

logger = logging.getLogger(__name__)


class InterviewPreparationService:

    def __init__(self, question_generator: QuestionGenerator):
        self.question_generator = question_generator

    def prepare_interview(self, *,
                          interview,
                          candidate: CandidateContextDTO,
                          vacancy: VacancyContextDTO,
                          questions_count: int) -> None:

        logger.info("Начало подготовки интервью %s для кандидата %s", interview.pk, candidate.id)

        # Генерация вопросов
        questions = self.question_generator.generate(
            vacancy_title=vacancy.job_title,
            vacancy_description=vacancy.prompt_description,
            candidate_resume=candidate.resume_text or "",
            questions_count=questions_count,
        )
        if not questions:
            logger.error(f"Не удалось сгенерировать вопросы для интервью {interview.pk}. "
                         f"Кандидат: {candidate.id}, Вакансия: {vacancy.id}")
            raise InterviewGenerationError()

        default_status = AnswerStatus.objects.get_pending()  # Всегда устанавливаем статус по-умолчанию (pending)

        for q in questions:
            InterviewQuestion.objects.create(
                interview=interview,
                question_text=q.text,
                order=q.order,
                status=default_status,
            )
        logger.info(f"Вопросы успешно созданы для интервью {interview.pk}")
