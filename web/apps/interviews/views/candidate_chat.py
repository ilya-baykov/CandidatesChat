
from django.shortcuts import get_object_or_404, render
from django.views import View

from ..models import Interview, InterviewQuestion
from ..services.flow import InterviewFlowService


class CandidateInterviewView(View):
    """
    MVP-View для чата кандидата.

    View:
    - ничего не решает
    - ничего не оркестрирует
    - просто делегирует Flow
    """

    template_name = "interviews/chat.html"

    @staticmethod
    def get_interview() -> Interview:
        """
        MVP-реализация.
        Позже будет поиск по token_link.
        """
        interview = (
            Interview.objects
            .select_related("candidate", "vacancy", "status")
            .prefetch_related("messages__role")
            .first()
        )
        return interview

    def get(self, request):
        interview = self.get_interview()
        flow = InterviewFlowService(interview=interview)

        state = flow.get_state_for_display()
        context = {"interview": interview, **state}
        return render(request, self.template_name, context)

    def post(self, request):
        interview = self.get_interview()
        flow = InterviewFlowService(interview=interview)

        question = get_object_or_404(InterviewQuestion, id=request.POST.get("question_id"), interview=interview)

        answer_text = request.POST.get("answer_text", "").strip()

        validation_result = flow.submit_answer(question=question, answer_text=answer_text)

        state = flow.get_state_for_display()
        context = {
            "interview": interview,
            "validation_result": validation_result,
            **state,
        }
        return render(request, self.template_name, context)
