from django.urls import path
from .views import CandidateInterviewView

app_name = "interviews"

urlpatterns = [
    path("chat/", CandidateInterviewView.as_view(), name="candidate_chat"),
]
