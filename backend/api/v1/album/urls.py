"""
    Album urls.
"""

from django.urls import path, include

from .routers import router

urlpatterns = [
    # api/v1/albums/
    # api/v1/albums/{pk}/

    # api/v1/downloads/{pk}/

    path('', include(router.urls))
]
