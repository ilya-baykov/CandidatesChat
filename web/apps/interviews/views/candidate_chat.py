from django.shortcuts import get_object_or_404, render
from django.views import View

from apps.interviews.models import Interview, InterviewQuestion
from apps.interviews.services.flow import InterviewFlowService


class CandidateInterviewView(View):
    """
    MVP-View для чата кандидата.

    View:
    - ничего не решает
    - ничего не оркестрирует
    - просто делегирует Flow и Celery
    """

    template_name = "interviews/chat.html"

    @staticmethod
    def get_interview() -> Interview:
        """
        MVP-реализация.
        Позже будет поиск по token_link.
        """
        return (
            Interview.objects
            .select_related("candidate", "vacancy", "status")
            .prefetch_related("messages__role")
            .first()
        )

    def get(self, request):
        interview = self.get_interview()
        flow = InterviewFlowService(interview=interview)

        state = flow.get_state_for_display()
        context = {
            "interview": interview,
            **state,
        }
        return render(request, self.template_name, context)

    def post(self, request, run_ai_validation_task=None):
        question_id = request.POST.get("question_id")
        answer_text = request.POST.get("answer_text", "").strip()

        interview = self.get_interview()
        flow = InterviewFlowService(interview=interview)

        question = get_object_or_404(
            InterviewQuestion,
            id=question_id,
            interview=interview,
        )

        #  Быстрый sync-шаг (Сохраняем ответ пользователя и обновляем статус вопроса)
        flow.submit_answer(
            question=question,
            answer_text=answer_text,
        )

        # Запуск async use-case (Проверяем ответ пользователя и проводим flow-обработки сообщения)
        # Логика класса InterviewAnswerProcessingService (см tasks.py)
        run_ai_validation_task.delay(
            interview_id=interview.pk,
            question_id=question.pk,
            answer_text=answer_text,
        )

        # Отрисовываем текущее состояние (без AI-результата)
        state = flow.get_state_for_display()
        context = {
            "interview": interview,
            **state,
        }

        return render(request, self.template_name, context)
