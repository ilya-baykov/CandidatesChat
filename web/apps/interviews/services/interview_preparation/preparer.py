from apps.interviews.models import InterviewQuestion
from apps.interviews.services.ai_question_generation.generator import QuestionGenerator
from apps.interviews.services.interview_preparation.dto import CandidateContextDTO, VacancyContextDTO
from apps.reference.models import AnswerStatus


class InterviewPreparationService:

    def __init__(self, question_generator: QuestionGenerator):
        self.question_generator = question_generator

    def prepare_interview(self, *,
                          interview,
                          candidate: CandidateContextDTO,
                          vacancy: VacancyContextDTO,
                          questions_count: int) -> None:
        questions = self.question_generator.generate(
            vacancy_title=vacancy.job_title,
            vacancy_description=vacancy.build_prompt_description,
            candidate_resume=candidate.resume_text or "",
            questions_count=questions_count,
        )

        default_status = AnswerStatus.objects.get_pending()  # Всегда устанавливаем статус по-умолчанию (pending)

        for q in questions:
            InterviewQuestion.objects.create(
                interview=interview,
                question_text=q.text,
                order=q.order,
                status=default_status,
            )
