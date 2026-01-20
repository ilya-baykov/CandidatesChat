from abc import ABC, abstractmethod

from apps.interviews.services.ai_question_generation.dto import GeneratedQuestion
from apps.interviews.services.ai_question_generation.prompts import PromptGenerator
from core.ai_service.clients import NeuralGatewayClient, gpt_4_model
from core.utilities.json_extractor import JsonExtractor


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

        prompt = PromptGenerator.generate_questions(
            vacancy_title=vacancy_title,
            vacancy_description=vacancy_description,
            candidate_resume=candidate_resume,
            questions_count=questions_count,
        )

        for _ in range(self.max_attempts):
            raw_text = self.client.get_answer(prompt)
            data = JsonExtractor.extract_json(raw_text)

            if not data:
                continue

            questions = data.get("questions")
            if not isinstance(questions, list):
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
                    continue

            if result:
                return result

        # fail-safe
        return []

ai_question_generator = AIQuestionGenerator(client=gpt_4_model)