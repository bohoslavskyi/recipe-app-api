from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import (
    User,
    Recipe,
    Tag,
)


class BaseTestCase(TestCase):
    def create_user(self, **params: dict) -> None:
        defaults: dict = {
            'email': 'test@example.com',
            'password': 'testpassword123',
        }
        defaults.update(params)

        return get_user_model().objects.create_user(**defaults)

    def create_recipe(self, user: User, **params: dict) -> Recipe:
        defaults: dict = {
            'title': 'Sample recipe title',
            'description': 'Sample recipe description',
            'price': Decimal('5.49'),
            'time_minutes': 25,
            'link': 'http://example.com/recipe.pdf',
        }
        defaults.update(params)

        return Recipe.objects.create(user=user, **defaults)

    def create_tag(self, name: str, user: User) -> Tag:
        return Tag.objects.create(name=name, user=user)
