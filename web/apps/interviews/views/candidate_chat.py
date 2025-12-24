from django.shortcuts import render, get_object_or_404
from django.views import View

from apps.interviews.models import Interview, InterviewQuestion
from apps.interviews.services.flow import InterviewFlowService
from apps.interviews.services.answer_validation.ai import ai_answer_validator
from apps.interviews.services.message_service import MessageService


class CandidateInterviewView(View):
    """
    MVP-View для чата кандидата.

    Flow:
    1. Показываем текущий вопрос (pending или repeat)
    2. Сохраняем сообщение кандидата
    3. Валидируем ответ через ИИ
    4. Сохраняем сообщение ИИ (если есть)
    5. Меняем статус вопроса
    6. Показываем следующий вопрос или завершаем интервью
    """

    template_name = "interviews/chat.html"

    @staticmethod
    def get_interview() -> Interview:
        """
        MVP-реализация.
        Позже будет поиск по token_link.
        """
        interview = (Interview.objects
                     .select_related("candidate", "vacancy", "status")
                     .prefetch_related("messages__role"))
        return interview.first()

    @staticmethod
    def build_context(*, interview: Interview, current_question: InterviewQuestion | None,
                      validation_result=None) -> dict:
        context = {
            "interview": interview,
            "messages": interview.messages.select_related("role").order_by("created_at"),  # noqa
            "current_question": current_question,
            "validation_result": validation_result
        }
        return context

    def get(self, request):
        interview = self.get_interview()

        flow = InterviewFlowService(interview=interview, answer_validator=ai_answer_validator)

        current_question = flow.get_current_question()

        if current_question:
            MessageService.ensure_system_question_logged(
                interview=interview,
                question=current_question,
            )

        context = self.build_context(interview=interview, current_question=current_question)

        return render(request, self.template_name, context)

    def post(self, request):
        interview = self.get_interview()

        flow = InterviewFlowService(interview=interview, answer_validator=ai_answer_validator)

        question_id = request.POST.get("question_id")
        answer_text = request.POST.get("answer_text", "").strip()

        question = get_object_or_404(InterviewQuestion, id=question_id, interview=interview)

        validation_result = flow.submit_answer(
            question=question,
            answer_text=answer_text,
            question_history=None,  # подключим позже
        )

        current_question = flow.get_current_question()
        if current_question:
            MessageService.ensure_system_question_logged(
                interview=interview,
                question=current_question,
            )

        context = self.build_context(interview=interview, current_question=current_question,
                                     validation_result=validation_result)

        return render(request, self.template_name, context)
