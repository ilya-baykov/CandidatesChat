from django.urls import path, include

from web.api.routers import router

urlpatterns = [
    path("", include(router.urls)),
]
