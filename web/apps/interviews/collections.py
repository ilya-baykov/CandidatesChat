from typing import Literal, TypeAlias
from enum import Enum


class AnswerCodes(Enum):
    PENDING = "pending"
    ANSWERED = "answered"
    VALIDATING = "validating"
    SCORED = "scored"
    REPEAT = "repeat"
    FAILED_VALIDATION = "failed_validation"


class InterviewCodes:
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED_PRECONDITION = "failed_precondition"


# Литералы для простого использования
AnswerCodeLiteral: TypeAlias = Literal[
    AnswerCodes.PENDING,
    AnswerCodes.VALIDATING,
    AnswerCodes.ANSWERED,
    AnswerCodes.SCORED,
    AnswerCodes.REPEAT,
    AnswerCodes.FAILED_VALIDATION,
]
