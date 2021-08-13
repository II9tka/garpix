import factory.fuzzy
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    email = "user@site.com"

    class Meta:
        model = User
        django_get_or_create = ("email",)
