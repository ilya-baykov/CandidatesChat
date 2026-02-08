from rest_framework.routers import DefaultRouter

from api.views.interviews.viewset import InterviewCommandViewSet, InterviewQueryViewSet, InterviewFrontViewSet

router = DefaultRouter()


# ── команды создания/изменения интервью
router.register(
    r"interviews",
    InterviewCommandViewSet,
    basename="interview-command",
)

# ── получение интервью (service-to-service API)
router.register(
    r"interviews/query",
    InterviewQueryViewSet,
    basename="interview-query",
)

# ── фронтенд ручки (summary)
router.register(
    r"interviews/front",
    InterviewFrontViewSet,
    basename="interview-front",
)