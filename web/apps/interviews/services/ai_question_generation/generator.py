import logging
from abc import ABC, abstractmethod

from apps.interviews.services.ai_question_generation.dto import GeneratedQuestion
from apps.interviews.services.ai_question_generation.prompts import PromptGenerator
from core.ai_service.clients import NeuralGatewayClient, gpt_4_model
from core.utilities.extractors.json_extractor import JsonExtractor

logger = logging.getLogger(__name__)


class QuestionGenerator(ABC):

    @abstractmethod
    def generate(self, *,
                 vacancy_title: str,
                 vacancy_description: str,
                 candidate_resume: str,
                 questions_count: int,
                 ) -> list[GeneratedQuestion]:
        raise NotImplementedError


class AIQuestionGenerator(QuestionGenerator):

    def __init__(self, client: NeuralGatewayClient, max_attempts: int = 3):
        self.client = client
        self.max_attempts = max_attempts

    def generate(self, *,
                 vacancy_title: str,
                 vacancy_description: str,
                 candidate_resume: str,
                 questions_count: int) -> list[GeneratedQuestion]:

        logger.info(f"Генерация вопросов через AI: вакансия {vacancy_title}")

        prompt = PromptGenerator.generate_questions(
            vacancy_title=vacancy_title,
            vacancy_description=vacancy_description,
            candidate_resume=candidate_resume,
            questions_count=questions_count,
        )

        for attempt in range(self.max_attempts):
            logger.debug(f"Попытка {attempt}: отправка запроса к AI")

            raw_text = self.client.get_answer(prompt)
            logger.info(f"AI_raw_text:{raw_text}")
            data = JsonExtractor.extract_json(raw_text)

            if not data:
                logger.warning(f"AI вернул пустой ответ:{raw_text}")
                continue

            questions = data.get("questions")
            if not isinstance(questions, list):
                logger.warning("AI вернул некорректный формат questions")
                continue

            result: list[GeneratedQuestion] = []

            for item in questions:
                try:
                    result.append(
                        GeneratedQuestion(
                            order=int(item["order"]),
                            text=str(item["text"]).strip(),
                        )
                    )
                except (KeyError, ValueError, TypeError):
                    logger.warning(f"Невалидный элемент вопроса от AI; item={item}")
                    continue

            if result:
                logger.info(f"AI вернул {len(result)} корректных вопросов")
                return result

        # fail-safe
        logger.error(f"Не удалось сгенерировать вопросы через AI после {self.max_attempts} попыток")
        return []


ai_question_generator = AIQuestionGenerator(client=gpt_4_model)
