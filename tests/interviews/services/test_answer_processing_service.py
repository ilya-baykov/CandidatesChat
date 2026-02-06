from unittest.mock import Mock

from apps.interviews.collections import AnswerCodes, MessageRoleCodes
from apps.interviews.services.constants import INTERVIEW_SAVED_MESSAGE


def test_apply_validation_correct_answer_sets_scored_status(service, validation_result):
    """
    Проверяет, что при правильном ответе статус вопроса устанавливается в SCORED.

    :param service: Экземпляр сервиса обработки ответов кандидата.
    :param validation_result: Фиктивный результат валидации с правильным ответом.
    """
    validation_result.is_correct = True

    answer = Mock()
    answer.attempt_count = 1
    service.answer_service.save.return_value = answer

    service._apply_validation_result(
        answer_text="Correct answer",
        validation_result=validation_result,
    )

    service.question_service.mark_status.assert_called_once_with(
        question=service.question,  # noqa
        code=AnswerCodes.SCORED,
    )


def test_apply_validation_incorrect_answer_repeat_if_attempts_left(service, validation_result):
    """
    Проверяет, что при неправильном ответе со слишком малым количеством попыток
    статус вопроса устанавливается в REPEAT.

    :param service: Экземпляр сервиса обработки ответов кандидата.
    :param validation_result: Фиктивный результат валидации с неправильным ответом.
    """
    validation_result.is_correct = False

    answer = Mock()
    answer.attempt_count = service.MAX_ATTEMPTS - 1
    service.answer_service.save.return_value = answer

    service._apply_validation_result(
        answer_text="Wrong answer",
        validation_result=validation_result,
    )

    service.question_service.mark_status.assert_called_once_with(
        question=service.question,  # noqa
        code=AnswerCodes.REPEAT,
    )


def test_apply_validation_incorrect_answer_scored_if_max_attempts_reached(service, validation_result):
    """
    Проверяет, что если максимальное количество попыток достигнуто,
    статус вопроса устанавливается в SCORED, даже для неправильных ответов.

    :param service: Экземпляр сервиса обработки ответов кандидата.
    :param validation_result: Фиктивный результат валидации с неправильным ответом.
    """
    validation_result.is_correct = False

    answer = Mock()
    answer.attempt_count = service.MAX_ATTEMPTS
    service.answer_service.save.return_value = answer

    service._apply_validation_result(
        answer_text="Wrong again",
        validation_result=validation_result,
    )

    service.question_service.mark_status.assert_called_once_with(
        question=service.question,  # noqa
        code=AnswerCodes.SCORED,
    )


def test_apply_validation_sends_agent_message_if_reply_exists(service, validation_result):
    """
    Проверяет, что, если в результате валидации есть ответное сообщение,
    оно отправляется.

    :param service: Экземпляр сервиса обработки ответов кандидата.
    :param validation_result: Фиктивный результат валидации с ответным сообщением.
    """
    validation_result.reply_message = "Please clarify your answer"

    answer = Mock()
    answer.attempt_count = 1
    service.answer_service.save.return_value = answer

    service._apply_validation_result(
        answer_text="Some answer",
        validation_result=validation_result,
    )

    service.message_service.add_message.assert_called_once()


def test_apply_validation_does_not_send_message_if_no_reply(service, validation_result):
    """
    Проверяет, что если нет ответного сообщения в результате валидации,
    сообщение не отправляется.

    :param service: Экземпляр сервиса обработки ответов кандидата.
    :param validation_result: Фиктивный результат валидации без ответного сообщения.
    """
    validation_result.reply_message = None

    answer = Mock()
    answer.attempt_count = 1
    service.answer_service.save.return_value = answer

    service._apply_validation_result(
        answer_text="Some answer",
        validation_result=validation_result,
    )

    service.message_service.add_message.assert_not_called()


def test_process_runs_full_answer_processing_flow(service):
    """
    process():
    - строит историю вопроса
    - вызывает AI-валидацию
    - применяет результат
    - проверяет завершение интервью
    """

    # --- arrange ---
    answer_text = "Candidate answer"

    history = ["previous message"]
    service.message_service.build_question_history.return_value = history

    validation_result = Mock()
    validation_result.score = 90
    validation_result.is_correct = True
    validation_result.reply_message = None

    service.AI_ANSWER_VALIDATOR = Mock()
    service.AI_ANSWER_VALIDATOR.validate.return_value = validation_result

    # Подменяем внутренние шаги — они тестируются отдельно
    service._apply_validation_result = Mock()
    service._advance_interview_if_needed = Mock()

    # --- act ---
    service.process(answer_text=answer_text)

    # --- assert ---
    service.message_service.build_question_history.assert_called_once_with(
        interview=service.interview,  # noqa
        question=service.question,  # noqa
    )

    service.AI_ANSWER_VALIDATOR.validate.assert_called_once_with(
        vacancy_title=service.vacancy.job_title,  # noqa
        vacancy_description=service.vacancy.prompt_description,  # noqa
        question=service.question,  # noqa
        answer_text=answer_text,
        question_history=history,
    )

    service._apply_validation_result.assert_called_once_with(
        answer_text=answer_text,
        validation_result=validation_result,
    )

    service._advance_interview_if_needed.assert_called_once()


def test_advance_interview_if_needed_completes_interview_and_notifies_candidate(service, mocker):
    """
    Если интервью завершено:
    - отправляется system-сообщение
    - кандидат помечается как прошедший интервью
    """

    # interview_service сообщает, что интервью завершено
    service.interview_service.complete_if_done.return_value = True

    mark_passed_mock = mocker.patch(
        "apps.interviews.services.answer_processing.OkoCandidateStatusService.mark_interview_passed"
    )

    service._advance_interview_if_needed()

    service.message_service.add_message.assert_called_once_with(
        interview=service.interview,  # noqa
        role_code=MessageRoleCodes.SYSTEM,  # noqa
        content=INTERVIEW_SAVED_MESSAGE,  # noqa
    )

    mark_passed_mock.assert_called_once_with(candidate_id=service.interview.candidate_id)  # noqa
