# web/apps/interviews/views.py

from django.shortcuts import get_object_or_404, render
from django.views import View
from django.utils import timezone

from .models import Interview, InterviewQuestion
from .services import InterviewFlowService, QuestionService


class CandidateInterviewView(View):
    """
    MVP-View для чата кандидата.
    - GET: показывает текущий вопрос и историю ответов
    - POST: сохраняет ответ и показывает следующий вопрос или сообщение о завершении интервью
    """

    template_name = "interviews/chat.html"

    def get_interview(self) -> Interview:
        """
        На MVP выбираем первое доступное интервью.
        Позже здесь будет фильтр по токену.
        """
        return Interview.objects.first()

    def get(self, request):
        interview = self.get_interview()
        # Получаем следующий pending вопрос
        question = QuestionService.get_next(interview)

        context = {
            "interview": interview,
            "current_question": question,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        interview = self.get_interview()

        question_id = request.POST.get("question_id")
        answer_text = request.POST.get("answer_text")

        question = get_object_or_404(InterviewQuestion, id=question_id)

        # Сохраняем ответ и обновляем статус через сервис
        flow = InterviewFlowService(interview)
        flow.submit_answer(question, answer_text)

        # Получаем следующий вопрос после отправки ответа
        next_question = QuestionService.get_next(interview)

        context = {
            "interview": interview,
            "current_question": next_question,
        }
        return render(request, self.template_name, context)
