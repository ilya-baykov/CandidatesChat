from .interfaces import AnswerValidator
from .dto import AnswerValidationResult


class FakeAnswerValidator(AnswerValidator):
    """
    MVP-валидатор:
    всегда считает ответ корректным.
    """

    def validate(self, *, question, answer_text, question_history=None) -> AnswerValidationResult:
        result = AnswerValidationResult(is_correct=True, reply_message=None)
        return result
