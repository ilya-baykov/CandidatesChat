import uuid
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.http import Http404

from api.serializers.interviews import InterviewCreateInputSerializer, InterviewDetailSerializer
from apps.interviews.models import Interview
from apps.interviews.services.interview_preparation.interview_creation import InterviewCreationService
from apps.interviews.services.interviews import InterviewService


class InterviewViewSet(viewsets.GenericViewSet):
    """
    ViewSet для работы с интервью (service-to-service API, в основном для ОКО).

    Поддерживаемые действия:
    • POST /interviews/ - создание или возврат существующего интервью
    • GET /interviews/by-token/ - получение по уникальному токену
    • GET /interviews/by-candidate-vacancy/ - получение по candidate_id + vacancy_id

    Примеры:
        POST /interviews/
        {"candidate_id": "1234","vacancy_id": "1234"}

        GET /interviews/by-token/?token=12345
        GET /interviews/by-candidate-vacancy/?candidate_id=1234&vacancy_id=1234
    """

    def create(self, request, *args, **kwargs):  # noqa
        """
        Создаёт новое интервью или возвращает уже существующее по паре candidate_id + vacancy_id.

        Поведение:
        • Если интервью с такой парой ещё не существует → создаётся → статус 201 Created
        • Если уже существует → возвращается существующее → статус 200 OK

        Возможные ошибки:
        • 400 Bad Request - невалидные входные данные
        • 500 Internal Server Error - ошибка при создании интервью
        """
        input_serializer = InterviewCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        # Создание интервью с вызовом celery-задачи на генерацию вопросов
        interview, created = InterviewCreationService.execute(
            candidate_id=input_serializer.validated_data['candidate_id'],
            vacancy_id=input_serializer.validated_data['vacancy_id']
        )

        output_serializer = InterviewDetailSerializer(interview)
        status_response = status.HTTP_201_CREATED if created else status.HTTP_200_OK

        return Response(data=output_serializer.data, status=status_response)

    @action(detail=False, methods=['GET'], url_path='by-token')
    def by_token(self, request):
        """
        Получение интервью по уникальному токену.

        Query-параметр:
            token (обязательный) — UUID токена интервью

        Возвращает:
        • 200 OK + данные интервью
        • 400 Bad Request — если токен не передан или некорректный
        • 404 Not Found — если токен не найден

        Пример: GET /interviews/by-token/?token=12345
        """
        token = request.query_params.get('token')
        if not token:
            raise ValidationError({'token': 'Параметр token обязателен'})

        # Валидация формата UUID
        try:
            uuid.UUID(token)
        except ValueError:
            raise ValidationError({'token': 'Некорректный формат UUID'})

        interview = get_object_or_404(Interview, token=token)
        serializer = InterviewDetailSerializer(interview)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='by-candidate-vacancy')
    def by_candidate_vacancy(self, request):
        """
        Получение интервью по паре candidate_id + vacancy_id.

        Query-параметры (оба обязательны):
            candidate_id — UUID кандидата
            vacancy_id   — UUID вакансии

        Возвращает:
        • 200 OK + данные интервью
        • 400 Bad Request — если параметры отсутствуют или некорректны
        • 404 Not Found — если интервью не найдено

        Пример: GET /interviews/by-candidate-vacancy/?candidate_id=123&vacancy_id=123
        """
        candidate_id = request.query_params.get('candidate_id')
        vacancy_id = request.query_params.get('vacancy_id')

        if not candidate_id or not vacancy_id:
            raise ValidationError({'detail': 'Требуются параметры candidate_id и vacancy_id'})

        # Безопасное получение с обработкой исключения
        try:
            interview = InterviewService.get_by_candidate_and_vacancy(
                candidate_id=candidate_id,
                vacancy_id=vacancy_id
            )
        except Interview.DoesNotExist:
            raise Http404("Интервью не найдено")

        serializer = InterviewDetailSerializer(interview)
        return Response(serializer.data)
