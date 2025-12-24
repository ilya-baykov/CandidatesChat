class PromptGenerator:
    """Генератор промптов для проверки ответа кандидата."""

    @staticmethod
    def validate_answer(*, question_text: str, user_answer: str, question_history: str | None = None) -> str:
        history_block = (
            f"\nИстория диалога:\n{question_history}\n"
            if question_history
            else ""
        )
        prompt = ("Ты — ассистент для проведения интервью.\n\n" +

                  "Вопрос:\n" +
                  question_text + "\n\n" +


                  "Ответ кандидата:\n" +
                  user_answer + "\n\n" +


                  history_block +

                  "Проанализируй ответ и верни JSON СТРОГО в следующем формате:\n\n" +

                  '{"is_correct": true | false,\n' +
                  ' "reply_message": "строка для кандидата, если ответ некорректен",\n' +
                  ' "justification": "краткое объяснение решения"}\n\n' +

                  "Никакого текста вне JSON.")
        return prompt.strip()
