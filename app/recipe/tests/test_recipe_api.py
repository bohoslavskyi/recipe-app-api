from decimal import Decimal

from django.urls import reverse
from django.http import HttpResponse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    User,
    Tag,
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)
from recipe.tests.base import BaseTestCase


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id: int) -> str:
    return reverse('recipe:recipe-detail', args=[recipe_id])


class PublicRecipeAPItests(BaseTestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()

    def test_auth_required(self) -> None:
        response: HttpResponse = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(BaseTestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()
        self.user: User = self.create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self) -> None:
        self.create_recipe(user=self.user)
        self.create_recipe(user=self.user)

        response: HttpResponse = self.client.get(RECIPES_URL)
        recipes: list[Recipe] = Recipe.objects.all().order_by('-id')
        serializer: RecipeSerializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_list_limited_to_user(self) -> None:
        other_user: User = self.create_user(
            email='other@example.com',
            password='testpass123',
        )
        self.create_recipe(user=other_user)
        self.create_recipe(user=self.user)

        response: HttpResponse = self.client.get(RECIPES_URL)
        recipes: list[Recipe] = Recipe.objects.filter(user=self.user)
        serializer: RecipeSerializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_recipe_detail(self) -> None:
        recipe: Recipe = self.create_recipe(user=self.user)
        url: str = detail_url(recipe.id)
        response: HttpResponse = self.client.get(url)
        serializer: RecipeDetailSerializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self) -> None:
        payload: dict = {
            'title': 'Sample recipe title',
            'price': Decimal('5.49'),
            'time_minutes': 30,
        }
        response: HttpResponse = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe: Recipe = Recipe.objects.get(id=response.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_pastial_update(self) -> None:
        original_link: str = 'http://example.com/recipe.pdf'
        recipe: Recipe = self.create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )
        payload = {
            'title': 'New sample recipe title'
        }
        url: str = detail_url(recipe.id)
        response: HttpResponse = self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)

    def test_full_update(self) -> None:
        recipe: Recipe = self.create_recipe(user=self.user)
        payload: dict = {
            'title': 'New sample recipe title',
            'description': 'New sample recipe description',
            'price': Decimal('10.00'),
            'time_minutes': 15,
            'link': 'http://example.com/new_recipe.pdf',
        }
        url: str = detail_url(recipe.id)
        response: HttpResponse = self.client.put(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self) -> None:
        new_user: User = self.create_user(
            email='new.user@example.com',
            password='testpass123',
        )
        recipe: Recipe = self.create_recipe(user=self.user)
        payload: dict = {
            'user': new_user.id,
        }
        url: str = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self) -> None:
        recipe: Recipe = self.create_recipe(user=self.user)
        url = detail_url(recipe.id)
        response: HttpResponse = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self) -> None:
        payload: dict = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal(2.49),
            'tags': [
                {'name': 'Thai'},
                {'name': 'Dinner'},
            ],
        }
        response: HttpResponse = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes: list[Recipe] = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe: Recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists: bool = Tag.objects.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tag(self) -> None:
        tag_indian: Tag = Tag.objects.create(user=self.user, name='Indian')
        payload: dict = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal(2.49),
            'tags': [
                {'name': 'Indian'},
                {'name': 'Breakfast'},
            ],
        }
        response: HttpResponse = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes: list[Recipe] = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe: Recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists: bool = Tag.objects.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)
