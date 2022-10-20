from core.models import Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAG_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    return reverse("recipe:recipe-detail", args=[tag_id])


def create_user(email="sampleuser@example.com", password="samplepass"):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_filtered_tags(self):
        other_user = create_user(
            email="user2@example.com", password="password2"
        )
        Tag.objects.create(user=other_user, name="Fruity")
        tag = Tag.objects.create(user=self.user, name="Spicy")

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name="After Dinner")

        print(Tag.objects.all())

        payload = {"name": "Dessert"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        print(Tag.objects.all())

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name="Breakfast")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
