from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class AdminTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email="testadmin@example.com", password="adminpass1234"
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testapss123",
            name="Test user",
        )

    def test_users_list(self):
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
