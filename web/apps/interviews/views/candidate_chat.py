from django.shortcuts import render, get_object_or_404
from django.views import View

from apps.interviews.models import Interview, InterviewQuestion
from apps.interviews.services import InterviewFlowService


class CandidateInterviewView(View):
    """
    MVP-View для чата кандидата.
    Flow:
    1. Показываем один текущий вопрос (pending или repeat)
    2. Сохраняем ответ
    3. Если ответ корректный → отмечаем answered и показываем следующий
    4. Если некорректный → помечаем repeat и показываем тот же вопрос снова
    5. Когда все вопросы answered → интервью завершено
    """

    template_name = "interviews/chat.html"

    def get_interview(self) -> Interview:
        """
        На MVP выбираем первое доступное интервью.
        Позже сюда будет фильтр по токену.
        """
        return Interview.objects.first()

    def get(self, request):
        interview = self.get_interview()
        flow = InterviewFlowService(interview)
        current_question = flow.get_current_question()

        context = {
            "interview": interview,
            "current_question": current_question,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        interview = self.get_interview()
        flow = InterviewFlowService(interview)

        question_id = request.POST.get("question_id")
        answer_text = request.POST.get("answer_text")

        question = get_object_or_404(InterviewQuestion, id=question_id)

        # ===== MVP: эмуляция проверки ответа =====
        # Пока ИИ нет — мы сами решаем, корректный ли ответ
        # Для теста можно менять на False, чтобы проверить повтор вопроса
        is_correct = True

        # Отправляем ответ через flow
        flow.submit_answer(question=question, answer_text=answer_text, is_correct=is_correct)

        # Получаем следующий вопрос для отображения
        current_question = flow.get_current_question()

        context = {
            "interview": interview,
            "current_question": current_question,
        }
        return render(request, self.template_name, context)
