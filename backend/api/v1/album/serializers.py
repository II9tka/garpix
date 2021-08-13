import magic

from django.conf import settings
from django.utils.translation import gettext as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.album.models import Photo, PhotoDownloadLink

ACCEPTED_FILE_MIMETYPES = settings.ACCEPTED_FILE_MIMETYPES
ACCEPTED_FILE_SIZE = settings.ACCEPTED_FILE_SIZE


class CreatePhotoSerializer(serializers.ModelSerializer):
    """
        CreatePhotoSerializer serializer.
    """

    def validate_image(self, value):
        """
        Validate image field.

        :param value: Photo.image
        :type value: Union[InMemoryUploadedFile, TemporaryUploadedFile]
        :return: image or raise error
        :rtype: Union[InMemoryUploadedFile, TemporaryUploadedFile]
        """

        mime_type = magic.from_buffer(value.read(), mime=True)

        if mime_type not in ACCEPTED_FILE_MIMETYPES:
            raise ValidationError(
                {'image': _('Image mime must be: %s' % ', '.join(ACCEPTED_FILE_MIMETYPES))}
            )
        if value.size > ACCEPTED_FILE_SIZE:
            raise ValidationError(
                {'image': _('Image size must be not more %i bytes' % ACCEPTED_FILE_SIZE)}
            )
        return value

    class Meta:
        model = Photo
        exclude = ('creator',)


class ListPhotoSerializer(CreatePhotoSerializer):
    """
        ListPhotoSerializer serializer.
    """

    class Meta(CreatePhotoSerializer.Meta):
        exclude = CreatePhotoSerializer.Meta.exclude + ('cropped_image', 'webp_image',)


class UpdatePhotoSerializer(serializers.ModelSerializer):
    """
        UpdatePhotoSerializer serializer.
    """

    class Meta:
        model = Photo
        exclude = ('creator',)
        read_only_fields = ('image',)


class PhotoDownloadLinkSerializer(serializers.ModelSerializer):
    """
        PhotoDownloadLink serializer.
    """

    url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='photo_download_link-detail'
    )

    class Meta:
        model = PhotoDownloadLink
        fields = ('id', 'url',)
        read_only_fields = ('url',)
