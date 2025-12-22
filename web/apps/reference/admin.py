from django.contrib import admin

from .models import AnswerStatus, InterviewStatus, MessageRole


@admin.register(InterviewStatus)
class InterviewStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "is_terminal", "is_active", "order")
    list_editable = ("order", "is_active", "is_terminal")
    search_fields = ("code", "title")
    ordering = ("order",)


@admin.register(AnswerStatus)
class AnswerStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "is_active", "order")
    list_editable = ("order", "is_active")
    search_fields = ("code", "title")
    ordering = ("order",)


@admin.register(MessageRole)
class MessageRoleAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "is_active", "order")
    list_editable = ("order", "is_active")
    search_fields = ("code", "title")
    ordering = ("order",)
