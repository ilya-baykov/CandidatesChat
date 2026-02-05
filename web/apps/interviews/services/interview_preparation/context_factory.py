import os
import logging
from typing import Optional
from django.core.cache import cache
from dataclasses import asdict
from apps.interviews.services.interview_preparation.dto import CandidateContextDTO, VacancyContextDTO
from core.integrations.oko.api.api_client import oko_client
from core.utilities.pdf_extractor import PDFTextExtractor

logger = logging.getLogger(__name__)


class InterviewContextFactory:
    VACANCY_CACHE_TTL = 60 * 60 * 12  # 12 часов
    CANDIDATE_CACHE_TTL = 60 * 60 * 2  # 2 часа

    @staticmethod
    def build_candidate(candidate_id: int) -> Optional[CandidateContextDTO]:
        cache_key = f"interview:candidate:{candidate_id}:v1"

        cached = cache.get(cache_key)
        if cached:
            return CandidateContextDTO(**cached)

        tmp_path = f"/tmp/resume_{candidate_id}.pdf"

        try:
            if not oko_client.download_candidate_resume(candidate_id, tmp_path):
                logger.warning("Не удалось скачать резюме кандидата %s", candidate_id)
                return None

            resume_text = PDFTextExtractor.get_text(tmp_path)
            candidate_context = CandidateContextDTO(id=candidate_id, resume_text=resume_text)

            # Сохраняем в кеш
            cache.set(cache_key, asdict(candidate_context),
                      timeout=InterviewContextFactory.CANDIDATE_CACHE_TTL, )
            return candidate_context
        except Exception as e:
            logger.exception("Ошибка при построении контекста кандидата %s", candidate_id, exc_info=e)
        finally:
            # удаляем временный файл
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception as e:
                    logger.warning("Не удалось удалить временный файл %s: %s", tmp_path, e)

    @staticmethod
    def build_vacancy(vacancy_id: int) -> Optional[VacancyContextDTO]:
        cache_key = f"interview:vacancy:{vacancy_id}:v1"

        cached = cache.get(cache_key)
        if cached:
            return VacancyContextDTO(**cached)

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
        cache.set(cache_key, asdict(vacancy), timeout=InterviewContextFactory.VACANCY_CACHE_TTL)
        return vacancy
