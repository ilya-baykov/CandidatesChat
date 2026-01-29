from django.db import models

from apps.interviews.collections import AnswerCodes


class AnswerStatusQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)

    def get_pending(self):
        """Явно получаем статус 'pending'."""
        return self.get(code=AnswerCodes.PENDING.value)