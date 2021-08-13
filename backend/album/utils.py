"""
    Contain functions, which do not belong to the class but are used by it.
"""


from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from moviepy.editor import ImageClip, ImageSequenceClip
from moviepy.video.fx.resize import resize

ACCEPTED_FILE_MIMETYPES = settings.ACCEPTED_FILE_MIMETYPES
EMAIL_HOST_USER = settings.EMAIL_HOST_USER


def change_file_extension(filename: str, extension: str) -> str:
    """
    Changed file extension to received extension

    :param filename: filename
    :type filename: str
    :param extension: file extension
    :type extension: str
    :return: new filename
    :rtype: str
    """
    return filename.split('.')[0] + extension


def make_movie(images, movie_path: str) -> bool:
    """
    Resize images to 800x600 and convert to .webm file

    :param images: Photo's QuerySet
    :type images: QuerySet[Photo]
    :param movie_path: media movie path
    :type movie_path: str
    :return: True
    :rtype: bool
    """

    frames = []
    paths = [photo.image.path for photo in images]

    for path in paths:
        frame = ImageClip(path).set_position(('center', 'center')).set_duration(1)
        resized_frame = resize(frame, newsize=(800, 600))

        frames.append(resized_frame.img)

    ImageSequenceClip(
        frames, fps=1
    ).set_duration(
        images.count()
    ).write_videofile(
        movie_path, fps=24
    )

    return True


def make_valid_format(file_format: str) -> str:
    """
    PIL thinks, that JPG format is not valid

    :param file_format: upper file extension
    :type file_format: str
    :return: received file format or JPEG
    :rtype: str
    """

    return file_format if file_format != 'JPG' else 'JPEG'


def mail_creator(emails, context):
    subject = 'New notification!'
    html_template = get_template('album/notification.html').render(context)
    txt_template = get_template('album/base.txt')

    message_alternatives = EmailMultiAlternatives(
        subject=subject,
        body=txt_template.template.source,
        from_email=EMAIL_HOST_USER,
        to=emails
    )

    message_alternatives.attach_alternative(html_template, "text/html")
    message_alternatives.send()
