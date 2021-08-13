from __future__ import annotations

import os
from io import BytesIO
from typing import Type

from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from backend.album.base import SingletonModel
from backend.album.utils import change_file_extension, make_valid_format

MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL

User = get_user_model()


def upload_to(file: Photo = None, filename: str = '') -> str:
    """
    upload_to handler.

    :param file: Photo's object
    :type file: Photo
    :param filename: file name
    :type filename: str
    :return: New media path to file
    :rtype: str
    """

    return 'uploads/%s' % filename


class PhotoDownloadLink(models.Model):
    """
        PhotoDownloadLink model.
    """

    file_name = models.CharField(
        max_length=100, verbose_name=_('File name'), editable=False
    )
    file_path = models.CharField(
        max_length=300, verbose_name=_('File path'), editable=False
    )

    @classmethod
    def make_link(cls) -> PhotoDownloadLink:
        """
        Make unique path link to movie.webm file.

        :return: PhotoDownloadLink object
        :rtype: PhotoDownloadLink
        """

        videos_path = os.path.join(MEDIA_ROOT, 'videos')

        if not os.path.isdir(videos_path):
            os.mkdir(videos_path)

        file_system_storage = FileSystemStorage()
        original_filepath = os.path.join(videos_path, 'movie.webm')
        unique_filepath = file_system_storage.get_available_name(original_filepath)
        file_name = unique_filepath.split('/')[-1]

        return cls.objects.create(
            file_path=unique_filepath, file_name=file_name
        )

    def __str__(self):
        return 'Download %s' % self.file_path

    class Meta:
        ordering = ('id',)
        verbose_name = _('Photo download link')
        verbose_name_plural = _('Photo download links')


class BestPhotoNotification(SingletonModel):
    """
        BestPhotoNotification model.
    """

    notification_text = models.TextField(
        blank=True, verbose_name=_('Notification text')
    )

    def __str__(self):
        return '%s' % self.__class__.__name__

    class Meta:
        ordering = ('id',)
        verbose_name = _('Best photo notification')
        verbose_name_plural = _('Best photo notifications')


class Photo(models.Model):
    """
        Photo model.
    """
    title = models.CharField(
        max_length=100, verbose_name=_('Title')
    )
    image = models.ImageField(
        upload_to=upload_to, verbose_name=_('Image')
    )
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('Creator'), related_name='photos'
    )
    cropped_image = models.ImageField(
        upload_to=upload_to, verbose_name=_('Image mini'), editable=False
    )
    webp_image = models.ImageField(
        upload_to=upload_to, verbose_name=_('Image webp'), editable=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Created at')
    )
    views = models.BigIntegerField(
        default=0, verbose_name=_('Views'), editable=False
    )

    def add_views_count(self) -> bool:
        """
        Add 1 view and save.

        :return: True
        :rtype: bool
        """

        self.views += 1
        self.save(update_fields=['views'])

        return True

    def save(self, *args, **kwargs):
        if self._is_first_creation():
            self.prepare_cropped_image()
            self.prepare_webp_image()

        super().save(*args, **kwargs)

    def prepare_cropped_image(self) -> bool:
        """
        Prepare cropped image before save.

        :return: True
        :rtype: bool
        """

        return self._make_image(
            'cropped_image'
        )

    def prepare_webp_image(self) -> bool:
        """
        Prepare webp image before save.

        :return: True
        :rtype: bool
        """

        filename = change_file_extension(self.image.name, '.webp')

        return self._make_image(
            'webp_image', file_format='WEBP', filename=filename
        )

    @classmethod
    def get_top_photos(cls) -> QuerySet[Photo]:
        """
        return QuerySet ordered by views.

        :return: Photo's QuerySet
        :rtype: QuerySet[Photo]
        """

        # Yes, it may be in Manager, but I'm lazy

        return cls.objects.order_by(
            '-views'
        ).only('image')[:10]

    @classmethod
    def get_top_user_photos(cls, user: User) -> QuerySet[Photo]:
        """
        return QuerySet ordered by views.

        :param user: User object
        :type user: User
        :return: Photo's QuerySet
        :rtype: QuerySet[Photo]
        """

        return cls.objects.filter(creator=user).order_by(
            '-views'
        ).only('image')[:10]

    def _is_first_creation(self) -> bool:
        """
        first creation checker.

        :return: True or False
        :rtype: bool
        """

        return not bool(
            self.webp_image and
            self.cropped_image
        )

    def _make_image(
            self,
            file_field_name: str,
            image: Image = None,
            file_format: str = '',
            filename: str = ''
    ) -> bool:
        """
        Make image to received file_field_name

        :param file_field_name: file field name for which need to save the image
        :type file_field_name: str
        :param image: new image logic or None
        :type image: Type[JpegImagePlugin]
        :param file_format: upper file format
        :type file_format: str
        :param filename: file name
        :type filename: str
        :return: True
        :rtype: bool
        """

        filename = filename if filename else self.image.name
        file_format = (
            file_format
            if file_format
            else make_valid_format(self.image.name.split('.')[-1].upper())
        )
        image = image if image else Image.open(self.image)

        image_io = BytesIO()

        image.save(image_io, quality=100, format=file_format)
        getattr(self, file_field_name).save(filename, ContentFile(image_io.getvalue()), save=False)

        return True

    def __str__(self):
        return 'Image %i: %s' % (self.id, self.image.name)

    class Meta:
        ordering = ('id',)
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')
