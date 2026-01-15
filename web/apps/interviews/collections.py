from typing import Literal, TypeAlias
from enum import Enum


class AnswerCodes(Enum):
    PENDING = "pending"
    ANSWERED = "answered"
    VALIDATING = "validating"
    SCORED = "scored"
    REPEAT = "repeat"


class InterviewCodes:
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# Литералы для простого использования
AnswerCodeLiteral: TypeAlias = Literal[
    AnswerCodes.PENDING,
    AnswerCodes.VALIDATING,
    AnswerCodes.ANSWERED,
    AnswerCodes.SCORED,
    AnswerCodes.REPEAT,
]
