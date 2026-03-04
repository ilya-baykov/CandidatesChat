from django.urls import path
from .views import ScheduleView

app_name = "interview_schedule"

urlpatterns = [
    path("schedule/<uuid:token>/", ScheduleView.as_view(), name="schedule"),
]
