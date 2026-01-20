from django.db import models


class AnswerStatusQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)

    def get_pending(self):
        """Явно получаем статус 'pending'."""
        return self.get(code="pending")