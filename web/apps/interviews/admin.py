from admin_extra_buttons.api import ExtraButtonsMixin,button
# from admin_extra_buttons.mixins import ExtraButtonsMixin
from django.contrib import admin
from django.http import HttpResponseRedirect
from .models import (
    Candidate,
    Vacancy,
    Interview,
    InterviewQuestion, InterviewMessage,
)
from .services.ai_question_generation.generator import ai_question_generator
from .services.interview_preparation import InterviewPreparationService


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    """Админка для кандидатов"""
    list_display = ("full_name", "external_id", "resume_text", "created_at")
    search_fields = ("full_name", "external_id", "contacts")
    ordering = ("full_name",)


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    """Админка для вакансий"""
    list_display = ("title", "vacancy_description", "external_id")
    search_fields = ("title", "vacancy_description", "external_id")
    ordering = ("title",)


class InterviewQuestionInline(admin.TabularInline):
    """
    Inline для вопросов интервью.
    Админ может добавлять вопросы, чтобы имитировать ИИ.
    """
    model = InterviewQuestion
    extra = 1  # показываем одну пустую форму для добавления
    can_delete = True
    show_change_link = True
    readonly_fields = ()  # пока все поля редактируемы


class InterviewMessageInline(admin.TabularInline):
    """
    Inline для просмотра истории сообщений интервью.
    Только для чтения.
    """
    model = InterviewMessage
    extra = 0
    can_delete = False
    readonly_fields = ("created_at", "role", "content")
    ordering = ("created_at",)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Interview)
class InterviewAdmin(ExtraButtonsMixin, admin.ModelAdmin):

    """
    Админка для интервью.
    Позволяет создавать интервью, добавлять вопросы.
    Ответы и сообщения пока не редактируются через админку.
    """
    list_display = ("id", "candidate", "vacancy", "status", "started_at", "completed_at", "total_score")
    search_fields = ("candidate__full_name", "candidate__external_id", "vacancy__title")
    list_filter = ("status", "vacancy")
    readonly_fields = ("token_link", "started_at", "completed_at", "total_score")
    inlines = [InterviewQuestionInline, InterviewMessageInline]
    ordering = ("-started_at",)

    @button(
        label="Сгенерировать вопросы",
        html_attrs={"style": "background-color:#e67e22; color:white; font-weight:bold;"},
        change_form=True,  # показывать только на странице редактирования
        change_list=False,  # не показывать на странице списка
    )
    def generate_questions(self, request, pk):
        """
        Генерация вопросов для интервью через Celery-задачу
        """
        try:
            interview = Interview.objects.select_related("candidate", "vacancy").get(id=pk)

            service = InterviewPreparationService(question_generator=ai_question_generator)
            service.prepare_interview(interview=interview, questions_count=5)

            self.message_user(request, "Задача на генерацию вопросов поставлена в очередь.", level="success")
        except Interview.DoesNotExist:
            self.message_user(request, "Интервью не найдено.", level="error")
        except Exception as e:
            self.message_user(request, f"Ошибка: {str(e)}", level="error")

        return HttpResponseRedirect(request.get_full_path())