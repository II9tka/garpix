import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from backend.album.factories import UserFactory

BASE_DIR = settings.BASE_DIR
MEDIA_ROOT = settings.MEDIA_ROOT


class RegistrationTestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('user-list')
        self.login_url = reverse('login')
        self.credentials = {
            'username': 'ctoiia',
            'email': 'fffxx@mail.ru',
            'password': 'c8846601'
        }

    def test_registration(self):
        response = self.client.post(self.register_url, self.credentials)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'email': 'fffxx@mail.ru', 'username': 'ctoiia', 'id': 1})

    def test_auth_token(self):
        self.client.post(self.register_url, self.credentials)
        data = {
            'username': 'ctoiia',
            'password': 'c8846601'
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('auth_token', response.json())


class PhotoTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.token = Token.objects.create(user=self.user)
        self.movie_url = reverse('album-make-movie-from-best-images')
        self.album_list_url = reverse('album-list')
        self.valid_image = (
            os.path.join(BASE_DIR, 'backend', 'album', 'fixtures', 'sunset.jpg')
        )
        self.invalid_image = (
            os.path.join(BASE_DIR, 'backend', 'album', 'fixtures', 'sunset.bmp')
        )

    def test_photo_list_as_authorized(self):
        self._make_authentication()
        response = self.client.get(self.album_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_photo_list_as_unauthorized(self):
        response = self.client.get(self.album_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_valid_photo_create(self):
        self._make_authentication()

        response = self._make_file('valid_image')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(os.path.isfile(os.path.join(MEDIA_ROOT, 'uploads', 'sunset.jpg')))
        self.assertTrue(os.path.isfile(os.path.join(MEDIA_ROOT, 'uploads', 'sunset.webp')))

    def test_invalid_photo_create(self):
        self._make_authentication()

        response = self._make_file('invalid_image')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_make_movie(self):
        self._make_authentication()
        self._make_file('valid_image')

        response = self.client.post(self.movie_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {'id': 1, 'url': 'http://testserver/api/v1/downloads/1/'})

    def test_download_movie(self):
        self._make_authentication()

        movie_response = self._make_movie()
        response = self.client.get(movie_response.json()['url'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers['Content-type'], 'audio/webm')

    def _make_authentication(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def _make_file(self, image_type: str):
        image_types = {
            'valid_image': self.valid_image,
            'invalid_image': self.invalid_image
        }

        with open(image_types[image_type], 'rb') as image:
            uploaded_image = SimpleUploadedFile(image_types[image_type], image.read())
            data = {
                'image': uploaded_image,
                'title': 'test title'
            }

            return self.client.post(self.album_list_url, data)

    def _make_movie(self):
        self._make_file('valid_image')
        return self.client.post(self.movie_url)
