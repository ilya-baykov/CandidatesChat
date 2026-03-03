from django.contrib import admin
from .models import InterviewSlot


@admin.register(InterviewSlot)
class InterviewSlotAdmin(admin.ModelAdmin):
    list_display = ("candidate_name", "candidate_email", "start_datetime", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("candidate_name", "candidate_email")
    readonly_fields = ("gmail_message_id", "created_at")
    ordering = ("-start_datetime",)
