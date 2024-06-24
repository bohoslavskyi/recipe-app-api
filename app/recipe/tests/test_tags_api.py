from django.urls import reverse
from django.http import HttpResponse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, User
from recipe.serializers import TagSerializer
from recipe.tests.base import BaseTestCase


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id: int) -> str:
    return reverse('recipe:tag-detail', args=[tag_id])


class PublicTagAPITests(BaseTestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()

    def test_auth_required(self) -> None:
        response: HttpResponse = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITest(BaseTestCase):
    def setUp(self) -> None:
        self.client: APIClient = APIClient()
        self.user: User = self.create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self) -> None:
        self.create_tag(name='Dessert', user=self.user)
        self.create_tag(name='Vegan', user=self.user)

        response: HttpResponse = self.client.get(TAGS_URL)
        tags: list[Tag] = Tag.objects.all().order_by('-name')
        serializer: TagSerializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self) -> None:
        other_user: User = self.create_user(email='other.user@example.com')
        self.create_tag(name='Fruity', user=other_user)
        tag: Tag = self.create_tag(name='Comfort Food', user=self.user)
        response: HttpResponse = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], tag.id)
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_update_tag(self) -> None:
        tag: Tag = self.create_tag(name='After Dinner', user=self.user)
        payload: dict = {'name': 'Dessert'}
        url: str = detail_url(tag.id)
        response: HttpResponse = self.client.patch(url, payload)
        serializer: TagSerializer = TagSerializer(tag)
        tag.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_delete_tag(self) -> None:
        tag: Tag = self.create_tag(name='After Dinner', user=self.user)
        url: str = detail_url(tag.id)
        response: HttpResponse = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(user=self.user).exists())
