from django.urls import path
from .views import ScheduleView, SuccessView

app_name = "interview_schedul"

urlpatterns = [
    path("schedule/", ScheduleView.as_view(), name="schedule"),
    path("success/", SuccessView.as_view(), name="success"),
]