import os
import requests
import logging
from typing import Optional

from core.integrations.oko.constants import OKO_BASE_URL

logger = logging.getLogger(__name__)


class OkoAPIClient:
    """Клиент для работы с API ОКО (вакансии, PDF-резюме кандидатов)."""

    BASE_URL_API = OKO_BASE_URL + "/api"
    HEADERS = {"Authorization": f"Basic {os.getenv('B64_CREDENTIALS')}"}

    def download_candidate_resume(self, candidate_id: int, target_path: str) -> bool:
        """
        Скачивает PDF-резюме кандидата.
        """
        url = f"{self.BASE_URL_API}/candidates/{candidate_id}/pdf/download/"
        try:
            logger.info("GET запрос (download resume): %s", url)
            response = requests.get(url, headers=self.HEADERS, stream=True, verify=False)

            if response.status_code != 200:
                logger.error(
                    "Ошибка при скачивании PDF кандидата %s: %s — %s",
                    candidate_id,
                    response.status_code,
                    response.text,
                )
                return False

            with open(target_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info("PDF-резюме кандидата %s успешно скачано", candidate_id)
            return True

        except Exception as exc:
            logger.exception(
                "Не удалось скачать резюме кандидата %s. Ошибка: %s",
                candidate_id,
                exc,
            )
            return False

    def get_vacancy(self, vacancy_id: int) -> Optional[dict]:
        """
        Получает данные вакансии (search-template).
        """
        url = f"{self.BASE_URL_API}/search-template/{vacancy_id}/"
        try:
            logger.info("GET запрос (vacancy): %s", url)
            response = requests.get(url, headers=self.HEADERS, verify=False)

            if response.status_code != 200:
                logger.error(
                    "Ошибка при получении вакансии %s: %s — %s",
                    vacancy_id,
                    response.status_code,
                    response.text,
                )
                return None

            return response.json()

        except Exception as exc:
            logger.exception(
                "Не удалось получить вакансию %s. Ошибка: %s",
                vacancy_id,
                exc,
            )
            return None


oko_client = OkoAPIClient()
