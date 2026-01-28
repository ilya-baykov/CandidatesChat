class InterviewError(Exception):
    pass


class InterviewPreconditionError(InterviewError):
    """Ошибка при создании интервью"""
    pass


class InterviewGenerationError(InterviewError):
    """Ошибка генерации вопросов"""
    pass
