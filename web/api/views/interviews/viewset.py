from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from api.exceptions import *
from api.serializers.interviews import *
from apps.interviews.services.ai_question_generation.dto import GeneratedQuestion
from apps.interviews.services.interview_preparation.interview_creation import InterviewCreationService
from apps.interviews.services.front.front_message_service import FrontInterviewService
from apps.interviews.services.interview_preparation.questions_strategies import PredefinedQuestionProvisionStrategy, \
    AIQuestionProvisionStrategy

from .mixins import InterviewByTokenMixin, InterviewByCandidateVacancyMixin
from .validators import Validator


class InterviewCommandViewSet(viewsets.GenericViewSet):
    """Команды изменения/создания интервью."""

    serializer_class = InterviewCreateInputSerializer

    @extend_schema(
        request=InterviewCreateInputSerializer,
        responses={
            201: InterviewDetailSerializer,
            404: OpenApiResponse(description="Кандидат или вакансия не найдены"),
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        raw_questions = serializer.validated_data.get("questions")
        if raw_questions:
            questions = [GeneratedQuestion(order=q["order"], text=q["text"]) for q in raw_questions]
            strategy = PredefinedQuestionProvisionStrategy(questions=questions)
        else:
            strategy = AIQuestionProvisionStrategy()

        try:
            interview, _ = InterviewCreationService.execute(
                candidate_id=serializer.validated_data["candidate_id"],
                vacancy_id=serializer.validated_data["vacancy_id"],
                strategy=strategy
            )
        except CandidateNotFound as exc:
            raise CandidateNotFoundAPIException(exc.candidate_id)

        except VacancyNotFound as exc:
            raise VacancyNotFoundAPIException(exc.vacancy_id)

        except InterviewAlreadyExists as exc:
            raise InterviewAlreadyExistsAPIException(exc.interview)

        output_serializer = InterviewDetailSerializer(interview)
        return Response(data=output_serializer.data, status=status.HTTP_201_CREATED)


class InterviewQueryViewSet(
    InterviewByTokenMixin,
    InterviewByCandidateVacancyMixin,
    viewsets.GenericViewSet,
):
    """Получение интервью."""

    serializer_class = InterviewDetailSerializer

    @extend_schema(
        parameters=[OpenApiParameter(name="token", type=str, required=True, description="UUID токена интервью")],
        responses={
            200: InterviewDetailSerializer,
            404: OpenApiResponse(description="Интервью не найдено")
        },
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
        serializer = self.get_serializer(interview)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="candidate_id", type=int, required=True),
            OpenApiParameter(name="vacancy_id", type=int, required=True),
        ],
        responses={
            200: InterviewDetailSerializer,
            404: OpenApiResponse(description="Интервью не найдено")
        },
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
        serializer = self.get_serializer(interview)
        return Response(serializer.data)


class InterviewFrontViewSet(
    InterviewByTokenMixin,
    InterviewByCandidateVacancyMixin,
    viewsets.GenericViewSet,
):
    """Методы для фронтенда."""

    serializer_class = FrontInterviewSummarySerializer

    @extend_schema(
        parameters=[OpenApiParameter(name="token", type=str, required=True)],
        responses={
            200: FrontInterviewSummarySerializer,
            404: OpenApiResponse(description="Интервью не найдено")
        },
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
        serializer = self.get_serializer(summary_data)
        return Response(serializer.data)

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
        serializer = self.get_serializer(summary_data)
        return Response(serializer.data)
