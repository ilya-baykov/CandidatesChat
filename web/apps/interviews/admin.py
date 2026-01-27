from admin_extra_buttons.api import ExtraButtonsMixin, button
from django.contrib import admin
from django.http import HttpResponseRedirect
from core.mixins.admin import RedirectToChangeMixin
from .models import Interview, InterviewQuestion, InterviewMessage
from ..interviews.tasks.triggers import start_generate_questions


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
class InterviewAdmin(RedirectToChangeMixin, ExtraButtonsMixin, admin.ModelAdmin):
    """
    Админка для интервью.
    Позволяет создавать интервью, добавлять вопросы.
    Ответы и сообщения пока не редактируются через админку.
    """
    list_display = ("id", "candidate_id", "vacancy_id", "status", "started_at", "completed_at", "total_score")
    readonly_fields = ("token", "started_at", "completed_at", "total_score")
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
            interview = Interview.objects.get(id=pk)

            if interview.questions.exists():  # noqa
                self.message_user(request, f"Ошибка: Вопросы для этого интервью уже сгенерированы. "
                                           f"Удалите существующие, если нужно перегенерировать.", level="error")
                return HttpResponseRedirect(self.redirect_to_change(pk))

            # Если проверка пройдена — ставим задачу в очередь
            start_generate_questions(interview_id=interview.pk, questions_count=5)

            self.message_user(request, "Задача на генерацию вопросов поставлена в очередь.", level="success")
        except Interview.DoesNotExist:
            self.message_user(request, "Интервью не найдено.", level="error")
        except Exception as e:
            self.message_user(request, f"Ошибка: {str(e)}", level="error")

        return HttpResponseRedirect(self.redirect_to_change(pk))
