import uuid
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.http import Http404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from api.exceptions import InterviewAlreadyExists, InterviewAlreadyExistsAPIException
from api.serializers.interviews import InterviewCreateInputSerializer, InterviewDetailSerializer, \
    FrontInterviewSummarySerializer
from apps.interviews.models import Interview
from apps.interviews.services.front.front_message_service import FrontInterviewService
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
    serializer_class = InterviewDetailSerializer  # Сериализатор по-умолчанию

    def get_serializer_class(self):
        if self.action == "create":
            return InterviewCreateInputSerializer
        return InterviewDetailSerializer

    @extend_schema(
        request=InterviewCreateInputSerializer,
        responses={
            201: InterviewDetailSerializer,
            409: OpenApiResponse(description="Интервью уже существует"),
            400: OpenApiResponse(description="Ошибка валидации входных данных"),
            500: OpenApiResponse(description="Ошибка создания интервью"),
        },
    )
    def create(self, request, *args, **kwargs):  # noqa
        """
        Создаёт новое интервью или вызывает ошибку если интервью уже существует по паре candidate_id + vacancy_id.

        Поведение:
        • Если интервью с такой парой ещё не существует → создаётся → статус 201 Created
        • Если уже существует → Ошибка 409

        Примечание:
        • Вопросы генерируются после создания интервью !
        Если по заданным параметрам не получится создать вопросы, то после выполнения функции по созданию вопросов,
        в Интервью проставится соответсвующий статус

        Возможные ошибки:
        • 400 Bad Request - невалидные входные данные
        • 409 Bad Request - Интервью уже существует
        • 500 Internal Server Error - ошибка при создании интервью
        """
        input_serializer = InterviewCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            # Создание интервью с вызовом celery-задачи на генерацию вопросов
            interview, created = InterviewCreationService.execute(
                candidate_id=input_serializer.validated_data['candidate_id'],
                vacancy_id=input_serializer.validated_data['vacancy_id'])

        except InterviewAlreadyExists as exc:
            raise InterviewAlreadyExistsAPIException(exc.interview)

        output_serializer = InterviewDetailSerializer(interview)
        return Response(data=output_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="token",
                type=str,
                location=OpenApiParameter.QUERY,  # noqa
                required=True,
                description="UUID токена интервью",
            ),
        ],
        responses={200: InterviewDetailSerializer},
    )
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="candidate_id",
                type=int,
                location=OpenApiParameter.QUERY,  # noqa
                required=True,
                description="ID кандидата (ОКО)",
            ),
            OpenApiParameter(
                name="vacancy_id",
                type=int,
                location=OpenApiParameter.QUERY,  # noqa
                required=True,
                description="ID вакансии (ОКО)",
            ),
        ],
        responses={200: InterviewDetailSerializer},
    )
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

    @extend_schema(
        parameters=[OpenApiParameter(
            name="token",
            type=str,
            required=True,
            description="UUID токена интервью",
        )],
        responses={200: FrontInterviewSummarySerializer},
    )
    @action(detail=False, methods=['GET'], url_path='summary')
    def summary(self, request):
        """
        Получение итоговой сводки интервью для фронтенда.

        Query-параметр:
            token (обязательный) — UUID токена интервью

        Возвращает:
        • 200 OK + полная сводка интервью
        • 400 Bad Request — если токен не передан или некорректный
        • 404 Not Found — если интервью не найдено
        """
        token = request.query_params.get('token')
        if not token:
            raise ValidationError({'token': 'Параметр token обязателен'})

        try:
            uuid.UUID(token)
        except ValueError:
            raise ValidationError({'token': 'Некорректный формат UUID'})

        interview = get_object_or_404(Interview, token=token)

        summary_data = FrontInterviewService.get_summary(interview)
        serializer = FrontInterviewSummarySerializer(summary_data)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="candidate_id",
                type=int,
                required=True,
                description="ID кандидата (ОКО)",
            ),
            OpenApiParameter(
                name="vacancy_id",
                type=int,
                required=True,
                description="ID вакансии (ОКО)",
            ),
        ],
        responses={200: FrontInterviewSummarySerializer},
    )
    @action(detail=False, methods=['GET'], url_path='summary-by-candidate-vacancy')
    def summary_by_candidate_vacancy(self, request):
        """
        Получение итоговой сводки интервью для фронтенда
        по паре candidate_id + vacancy_id.

        Query-параметры (оба обязательны):
            candidate_id — UUID кандидата
            vacancy_id   — UUID вакансии

        Возвращает:
        • 200 OK + полная сводка интервью
        • 400 Bad Request — если параметры отсутствуют или некорректны
        • 404 Not Found — если интервью не найдено

        Пример: GET /interviews/summary-by-candidate-vacancy/?candidate_id=123&vacancy_id=123
        """
        candidate_id = request.query_params.get('candidate_id')
        vacancy_id = request.query_params.get('vacancy_id')

        if not candidate_id or not vacancy_id:
            raise ValidationError({'detail': 'Требуются параметры candidate_id и vacancy_id'})

        # Получаем интервью через сервис
        try:
            interview = InterviewService.get_by_candidate_and_vacancy(
                candidate_id=candidate_id,
                vacancy_id=vacancy_id
            )
        except Interview.DoesNotExist:
            raise Http404("Интервью не найдено")

        # Получаем сводку через FrontInterviewService
        summary_data = FrontInterviewService.get_summary(interview)
        serializer = FrontInterviewSummarySerializer(summary_data)
        return Response(serializer.data)
