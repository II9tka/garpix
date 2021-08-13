import os
import random
import string

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import BaseCommand

from backend.album.models import Photo

User = get_user_model()
BASE_DIR = settings.BASE_DIR


def random_char(char_num: int) -> str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(char_num))


class Command(BaseCommand):
    help = 'Create initial data'

    def handle(self, *args, **kwargs):
        image_url = os.path.join(BASE_DIR, 'backend', 'album', 'fixtures', 'sunset.jpg')
        [
            User.objects.create(
                password=random.choice((10000000, 1000000000)),
                email=random_char(6) + '@gmail.com',
                username=random_char(10)
            ) for _ in range(5)
        ]

        with open(image_url, 'rb') as image:
            Photo.objects.create(
                image=SimpleUploadedFile(image_url, image.read()),
                views=random.choice((0, 100)),
                creator=random.choice(User.objects.all())
            )
