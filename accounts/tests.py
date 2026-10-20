
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountTests(TestCase):
    def test_registration_page_loads(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 200)

    def test_user_can_register(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "StrongTestPassword123!",
                "password2": "StrongTestPassword123!",
            },
        )

        self.assertTrue(
            User.objects.filter(username="testuser").exists()
        )
        self.assertRedirects(
            response,
            reverse("account_profile"),
        )

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username="existinguser",
            email="test@example.com",
            password="ExistingPassword123!",
        )

        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "TEST@example.com",
                "password1": "StrongTestPassword123!",
                "password2": "StrongTestPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(username="newuser").exists()
        )

    def test_invalid_registration_does_not_create_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "invaliduser",
                "email": "not-an-email",
                "password1": "StrongTestPassword123!",
                "password2": "DifferentPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(username="invaliduser").exists()
        )

    def test_profile_requires_login(self):
        response = self.client.get(reverse("account_profile"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('account_profile')}",
        )

    def test_authenticated_user_can_access_profile(self):
        user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="ProfilePassword123!",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("account_profile"))

        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)

    def test_user_can_log_in(self):
        User.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password="LoginPassword123!",
        )

        response = self.client.post(
            reverse("login"),
            {
                "username": "loginuser",
                "password": "LoginPassword123!",
            },
        )

        self.assertRedirects(
            response,
            reverse("account_profile"),
        )

    def test_logout_requires_post(self):
        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 405)

    def test_authenticated_user_can_log_out(self):
        user = User.objects.create_user(
            username="logoutuser",
            email="logout@example.com",
            password="LogoutPassword123!",
        )
        self.client.force_login(user)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, "/")
        self.assertNotIn("_auth_user_id", self.client.session)
