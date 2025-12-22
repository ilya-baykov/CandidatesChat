from django.db import models


class Vacancy(models.Model):
    """
    Кэшированная вакансия из внешней системы.
    Содержит только ID и название вакансии.
    """
    external_id = models.CharField(max_length=255, unique=True, verbose_name="Внешний ID")
    title = models.CharField(max_length=255, verbose_name="Название вакансии")

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

    def __str__(self):
        return self.title
