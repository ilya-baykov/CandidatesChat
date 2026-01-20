from django.db import models


class AnswerStatusQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)

    def default(self):
        """
        Возвращает статус по умолчанию для нового вопроса.
        """
        return self.active().order_by("order").first()
