from rest_framework.routers import DefaultRouter

from api.views.interviews import InterviewViewSet

router = DefaultRouter()

router.register(
    r"interviews",
    InterviewViewSet,
    basename="interview",
)
