from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from api.exceptions import InterviewAlreadyExistsAPIException, InterviewAlreadyExists
from api.serializers.interviews import *
from apps.interviews.services.interview_preparation.interview_creation import InterviewCreationService
from apps.interviews.services.front.front_message_service import FrontInterviewService

from .mixins import InterviewByTokenMixin, InterviewByCandidateVacancyMixin
from .validators import Validator


# TODO: Разделить InterviewViewSet

class InterviewViewSet(
    InterviewByTokenMixin,
    InterviewByCandidateVacancyMixin,
    viewsets.GenericViewSet,
):
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
    serializer_class = InterviewDetailSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return InterviewCreateInputSerializer
        return InterviewDetailSerializer

    # ── CREATE ───────────────────────────────────────────────

    @extend_schema(
        request=InterviewCreateInputSerializer,
        responses={
            201: InterviewDetailSerializer,
            409: OpenApiResponse(description="Интервью уже существует"),
            400: OpenApiResponse(description="Ошибка валидации входных данных"),
            500: OpenApiResponse(description="Ошибка создания интервью"),
        },
    )
    def create(self, request, *args, **kwargs):
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
        serializer = InterviewCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            interview, created = InterviewCreationService.execute(
                candidate_id=serializer.validated_data["candidate_id"],
                vacancy_id=serializer.validated_data["vacancy_id"],
            )
        except InterviewAlreadyExists as exc:
            raise InterviewAlreadyExistsAPIException(exc.interview)

        output_serializer = InterviewDetailSerializer(interview)
        return Response(data=output_serializer.data, status=status.HTTP_201_CREATED)

    # ── BY TOKEN ─────────────────────────────────────────────

    @extend_schema(
        parameters=[
            OpenApiParameter(name="token", type=str, required=True, description="UUID токена интервью"),
        ],
        responses={200: InterviewDetailSerializer},
    )
    @action(detail=False, methods=["GET"], url_path="by-token")
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
        token = request.query_params.get("token")
        interview = self.get_interview_by_token(token)
        return self.respond_with_interview(interview)

    # ── BY CANDIDATE + VACANCY ───────────────────────────────

    @extend_schema(
        parameters=[
            OpenApiParameter(name="candidate_id", type=int, required=True),
            OpenApiParameter(name="vacancy_id", type=int, required=True),
        ],
        responses={200: InterviewDetailSerializer},
    )
    @action(detail=False, methods=["GET"], url_path="by-candidate-vacancy")
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
        c_id, v_id = Validator.validate_candidate_vacancy_params(
            request.query_params.get("candidate_id"),
            request.query_params.get("vacancy_id"),
        )
        interview = self.get_interview_by_candidate_vacancy(c_id, v_id)
        return self.respond_with_interview(interview)

    # ── SUMMARY ──────────────────────────────────────────────

    @extend_schema(
        parameters=[OpenApiParameter(name="token", type=str, required=True)],
        responses={200: FrontInterviewSummarySerializer},
    )
    @action(detail=False, methods=["GET"], url_path="summary")
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
        token = request.query_params.get("token")
        Validator.validate_uuid(token)  # только валидация формата
        interview = self.get_interview_by_token(token)
        summary_data = FrontInterviewService.get_summary(interview)
        return Response(FrontInterviewSummarySerializer(summary_data).data)

    # ── SUMMARY BY CANDIDATE + VACANCY ───────────────────────

    @extend_schema(
        parameters=[
            OpenApiParameter(name="candidate_id", type=int, required=True),
            OpenApiParameter(name="vacancy_id", type=int, required=True),
        ],
        responses={200: FrontInterviewSummarySerializer},
    )
    @action(detail=False, methods=["GET"], url_path="summary-by-candidate-vacancy")
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
        c_id, v_id = Validator.validate_candidate_vacancy_params(
            request.query_params.get("candidate_id"),
            request.query_params.get("vacancy_id"),
        )
        interview = self.get_interview_by_candidate_vacancy(c_id, v_id)
        summary_data = FrontInterviewService.get_summary(interview)
        return Response(FrontInterviewSummarySerializer(summary_data).data)
