import json
import os
from abc import ABC, abstractmethod
from typing import Optional
import requests


class NeuralGatewayClient(ABC):
    """
    Базовый клиент нейрошлюза.
    Отвечает ТОЛЬКО за HTTP и получение текста ответа.
    """

    BASE_URL = "https://ai.rt.ru/api/1.0"

    TOKEN = os.getenv("NEURAL_GATEWAY_TOKEN")
    HEADERS = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    MODEL = None
    URL = None
    TEMPERATURE = 0

    def get_answer(self, prompt: str) -> Optional[str]:
        request_data = self._create_request_data(prompt)

        try:
            response = requests.post(
                self.URL,
                headers=self.HEADERS,
                data=json.dumps(request_data),
                timeout=10,  # важно
            )
            response.raise_for_status()

            response_data = response.json()
            return self._extract_text(response_data)

        except Exception as exc:
            return None

    @abstractmethod
    def _create_request_data(self, prompt: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def _extract_text(self, response_data: dict | list) -> Optional[str]:
        raise NotImplementedError


class ChatGPTClient(NeuralGatewayClient):
    MODEL = "gpt-4o-mini"
    URL = f"{NeuralGatewayClient.BASE_URL}/chatgpt/chat"

    def _create_request_data(self, prompt: str) -> dict:
        return {
            "chat": {
                "model": self.MODEL,
                "temperature": self.TEMPERATURE,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                        "type": "msg",
                    }
                ],
            }
        }

    def _extract_text(self, response_data) -> Optional[str]:
        try:
            return response_data[0]["message"]["content"]
        except Exception:
            return None
