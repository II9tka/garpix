from celery import shared_task

from backend.album.models import BestPhotoNotification, Photo
from backend.album.utils import mail_creator


@shared_task
def send_message() -> bool:
    text = BestPhotoNotification.load().notification_text
    emails = list(set([photo.creator.email for photo in Photo.get_top_photos()[:3] if photo]))

    if emails:
        context = {
            'text': text
        }

        mail_creator(emails, context)
        return True
    return False
