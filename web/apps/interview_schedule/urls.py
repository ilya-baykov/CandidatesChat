from django.urls import path
from .views import ScheduleView, SuccessView

app_name = "interview_schedule"

urlpatterns = [
    path("schedule/", ScheduleView.as_view(), name="schedule"),
    path("success/", SuccessView.as_view(), name="success"),
]