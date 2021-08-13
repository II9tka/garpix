"""
    Album views.
"""
from django.http import HttpResponse
from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.album.models import Photo, PhotoDownloadLink
from backend.album.utils import make_movie
from .permissions import IsOwnerOrReadOnlyIfAuthenticated
from .serializers import (
    UpdatePhotoSerializer,
    CreatePhotoSerializer,
    ListPhotoSerializer,
    PhotoDownloadLinkSerializer,
)


class PhotoDownloadLinkViewSet(mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    """
        PhotoDownloadLink ViewSet.
    """

    permission_classes = (permissions.IsAuthenticated,)
    queryset = PhotoDownloadLink.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """ Download file. """

        file_path = self.get_object().file_path
        file_name = self.get_object().file_name

        with open(file_path, 'rb') as file:
            response = HttpResponse(file, content_type='audio/webm')
            response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
            return response


class PhotoViewSet(viewsets.ModelViewSet):
    """
        PhotoViewSet ViewSet.
    """

    permission_classes = (IsOwnerOrReadOnlyIfAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            if self.get_object().creator == self.request.user:
                return UpdatePhotoSerializer
        elif self.action == 'create':
            return CreatePhotoSerializer
        return ListPhotoSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        instance.add_views_count()
        return Response(serializer.data)

    def get_queryset(self):
        return Photo.objects.all()

    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user
        )

    @action(
        methods=['POST'], detail=False, url_path='make_movie',
        permission_classes=(permissions.IsAuthenticated,)
    )
    @swagger_auto_schema(responses={200: PhotoDownloadLinkSerializer()})
    def make_movie_from_best_images(self, request):
        top_photos = Photo.get_top_photos()

        return self._make_request(top_photos, request)

    @action(
        methods=['POST'], detail=False, url_path='make_user_movie',
        permission_classes=(permissions.IsAuthenticated,)
    )
    @swagger_auto_schema(responses={200: PhotoDownloadLinkSerializer()})
    def make_movie_from_best_user_images(self, request):
        top_photos = Photo.get_top_user_photos(request.user)

        return self._make_request(top_photos, request)

    @staticmethod
    def _make_request(photos, request):
        """
        Validate Photos and return Request.

        :param photos: Photo's QuerySet
        :type photos: QuerySet[Photo]
        :param request: Request
        :type request: Request
        :return: Response
        :rtype: Response
        """

        if photos.count():
            link = PhotoDownloadLink.make_link()
            file_path = link.file_path

            make_movie(photos, file_path)

            serializer = PhotoDownloadLinkSerializer(link, context={'request': request})

            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(
            {'server': _('Photos does not exists')}, status=status.HTTP_400_BAD_REQUEST
        )
