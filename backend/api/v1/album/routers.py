from rest_framework import routers

from backend.api.v1.album.views import PhotoViewSet, PhotoDownloadLinkViewSet

router = routers.DefaultRouter()

router.register(r'albums', PhotoViewSet, basename='album')
router.register(r'downloads', PhotoDownloadLinkViewSet, basename='photo_download_link')
