from django.db import models


class InterviewStatus(models.Model):
    """
    Справочный статус интервью (диалога с кандидатом).

    Используется как состояние конечного автомата (FSM) интервью.
    Хранится в БД, чтобы:
    - статусы можно было расширять без изменения кода
    - управлять терминальностью процесса
    - использовать единый справочник во всех сервисах

    Поле `code` является машинным идентификатором и используется
    в бизнес-логике (НЕ id и НЕ title).
    """

    code = models.CharField(
        max_length=32,
        unique=True,
        help_text=(
            "Машинный код статуса. "
            "Используется в логике приложения (например: draft, in_progress, completed)."
        ),
    )

    title = models.CharField(
        max_length=64,
        help_text="Человекочитаемое название статуса для админки и UI.",
    )

    is_terminal = models.BooleanField(
        default=False,
        help_text=(
            "Признак терминального статуса. "
            "Если True — интервью считается завершённым, переходы запрещены."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Флаг активности статуса. "
            "Неактивные статусы не должны использоваться в новых интервью."
        ),
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Порядок отображения в админке и интерфейсах. "
            "Не используется для бизнес-логики переходов."
        ),
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Статус интервью"
        verbose_name_plural = "Статусы интервью"

    def __str__(self) -> str:
        return self.title


class AnswerStatus(models.Model):
    """
    Справочный статус ответа кандидата на конкретный вопрос.

    Используется для отслеживания жизненного цикла ответа:
    - ожидает ли ответ
    - получен ли ответ от кандидата
    - обработан / оценён ли ИИ-агентом
    """

    code = models.CharField(
        max_length=32,
        unique=True,
        help_text=(
            "Машинный код статуса ответа "
            "(например: pending, answered, scored)."
        ),
    )

    title = models.CharField(
        max_length=64,
        help_text="Человекочитаемое название статуса ответа.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Флаг активности статуса. "
            "Неактивные статусы не должны назначаться новым ответам."
        ),
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Порядок отображения в админке.",
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Статус ответа"
        verbose_name_plural = "Статусы ответов"

    def __str__(self) -> str:
        return self.title


class MessageRole(models.Model):
    """
    Справочный словарь ролей участников диалога в интервью.

    Используется для типизации сообщений в InterviewMessage.
    Хранится в БД, чтобы:
    - легко добавлять новые роли без изменения кода
    - управлять отображением и порядком в интерфейсах
    - иметь единый источник истины для всех сервисов

    Поле `code` — машинный идентификатор, используется в бизнес-логике.
    """

    code = models.CharField(
        max_length=32,
        unique=True,
        help_text=(
            "Машинный код роли. "
            "Используется в коде приложения (например: candidate, agent, system)."
        ),
    )

    title = models.CharField(
        max_length=64,
        help_text="Человекочитаемое название роли для админки и UI.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Флаг активности. Неактивные роли не должны использоваться в новых сообщениях."
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Порядок отображения в админке, фильтрах и интерфейсах."
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Роль сообщения"
        verbose_name_plural = "Роль сообщений"

    def __str__(self) -> str:
        return self.title
