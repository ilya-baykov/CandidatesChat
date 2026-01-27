from typing import Optional

from apps.interviews.services.interview_preparation.dto import CandidateContextDTO, VacancyContextDTO
from core.integrations.oko.client import oko_client
from core.utilities.pdf_extractor import PDFTextExtractor


class InterviewContextFactory:

    @staticmethod
    def build_candidate(candidate_id: int) -> Optional[CandidateContextDTO]:
        tmp_path = f"/tmp/resume_{candidate_id}.pdf"

        if not oko_client.download_candidate_resume(candidate_id, tmp_path):
            return None

        resume_text = PDFTextExtractor.get_text(tmp_path)
        return CandidateContextDTO(id=candidate_id, resume_text=resume_text)

    @staticmethod
    def build_vacancy(vacancy_id: int) -> Optional[VacancyContextDTO]:
        vacancy = oko_client.get_vacancy(vacancy_id)
        if not vacancy:
            return None

        vacancy = VacancyContextDTO(
            id=vacancy["id"],
            title=vacancy.get("vacancy", ""),
            city=vacancy.get("city", ""),
            job_title=vacancy.get("job_title", ""),
            main_responsibilities=vacancy.get("main_responsibilities", ""),
            required_experience=vacancy.get("required_experience", ""),
            software_knowledge=vacancy.get("software_knowledge", ""),
            wishes_prompt=vacancy.get("wishes_prompt", ""),
        )

        return vacancy
