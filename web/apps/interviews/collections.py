from typing import Literal, TypeAlias, TypedDict, Final, NamedTuple, Optional
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
    PENDING_QUESTIONS = "pending_questions"


class MessageRoleCodes:
    SYSTEM = "system"
    AGENT = "agent"
    CANDIDATE = "candidate"


# Литералы для простого использования
AnswerCodeLiteral: TypeAlias = Literal[
    AnswerCodes.PENDING,
    AnswerCodes.VALIDATING,
    AnswerCodes.ANSWERED,
    AnswerCodes.SCORED,
    AnswerCodes.REPEAT,
    AnswerCodes.FAILED_VALIDATION,
]


# Используются только для формирования данных для fron
class FrontMessageRoleCodes:
    ASSISTANT: Final = "assistant"
    CANDIDATE: Final = "candidate"


FrontSenderType: TypeAlias = Literal[
    FrontMessageRoleCodes.ASSISTANT,  # noqa
    FrontMessageRoleCodes.CANDIDATE  # noqa
]


class FrontDialogueMessage(TypedDict):
    sender: FrontSenderType  # noqa
    content: str
    created_at: str  # ISO 8601 строка, например "2025-02-06T14:35:22.123456+00:00"


class MessageDates(NamedTuple):
    first: Optional[str]
    last: Optional[str]


class FrontInterviewSummary(TypedDict):
    candidate_id: int
    vacancy_id: int
    current_status: str
    first_message_date: Optional[str]
    last_message_date: Optional[str]
    total_score: Optional[float]
    started_at: Optional[str]
    completed_at: Optional[str]
    is_completed: bool
    is_in_progress: bool
    dialogue_history: list[FrontDialogueMessage]
