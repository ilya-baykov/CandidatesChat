from django.urls import path
from apps.interviews.views.candidate_chat import CandidateInterviewView

app_name = "interviews"

urlpatterns = [
    path("chat/", CandidateInterviewView.as_view(), name="candidate_chat"),
]
