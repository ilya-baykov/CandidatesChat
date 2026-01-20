from django.contrib import admin
from .models import (
    Candidate,
    Vacancy,
    Interview,
    InterviewQuestion, InterviewMessage,
)


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
class InterviewAdmin(admin.ModelAdmin):
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
