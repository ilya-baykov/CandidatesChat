from django.db import models


# class Candidate(models.Model):
#     """
#     Снимок кандидата на момент интервью.
#     Используется для связывания интервью с внешней системой.
#     """
#     external_id = models.CharField(
#         max_length=64,
#         unique=True,
#         help_text="ID кандидата во внешней системе"
#     )
#     full_name = models.CharField(max_length=255, help_text="ФИО кандидата")
#     contacts = models.CharField(max_length=255, null=True, blank=True, help_text="Контакты кандидата")
#     resume_text = models.TextField(null=True, blank=True, help_text="Текст резюме кандидата")
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         verbose_name = "Кандидат"
#         verbose_name_plural = "Кандидаты"
#
#     def __str__(self):
#         return f"{self.full_name} ({self.external_id})"
