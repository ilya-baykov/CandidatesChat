from django.shortcuts import get_object_or_404, render, redirect
from django.views import View

from apps.interviews.models import Interview, InterviewQuestion
from apps.interviews.services.consent_processing_service import ConsentProcessingService
from apps.interviews.services.flow import InterviewFlowService
from apps.interviews.services.interviews import InterviewService
from apps.interviews.services.questions import QuestionService
from apps.interviews.tasks.triggers import start_answer_validation


class CandidateInterviewView(View):
    """
    MVP-View для чата кандидата.

    View:
    - ничего не решает
    - делегирует Flow и Celery для обычных вопросов
    - consent обрабатывает синхронно (до redirect, чтобы избежать race condition)
    """

    template_name = "interviews/chat.html"

    def get_interview(self) -> Interview:
        """Получение уникального интервью для конкретного кандидата (по токену чата)"""
        return get_object_or_404(
            Interview.objects
            .select_related("status")
            .prefetch_related("messages__role"),
            token=self.kwargs["token"],
        )

    def get(self, request, *args, **kwargs):
        interview = self.get_interview()
        flow = InterviewFlowService(interview=interview)
        state = flow.get_state_for_display()
        context = {
            "interview": interview,
            **state,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        interview = self.get_interview()

        # Защита от отправки сообщений в закрытое интервью
        if not InterviewService.is_active(interview):
            return redirect(request.path)

        question_id = request.POST.get("question_id")
        answer_text = request.POST.get("answer_text", "").strip()

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

        # Consent обрабатываем синхронно — результат нужен до redirect
        if QuestionService.is_consent_question(question):
            ConsentProcessingService(interview=interview, question=question).process(answer_text)
        else:
            start_answer_validation(
                interview_id=interview.pk,
                question_id=question.pk,
                answer_text=answer_text,
            )
        return redirect(request.path)
