from rest_framework.routers import DefaultRouter

from api.views.interviews.viewset import InterviewViewSet

router = DefaultRouter()

router.register(
    r"interviews",
    InterviewViewSet,
    basename="interview",
)
