from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse

from .forms import LoginForm, RegisterForm, ChangePasswordForm
from .models import User


class RegisterUserTest(TestCase):
    def setUp(self):
        self.user = {
            "username": "abeshek",
            "first_name": "Abhishek",
            "middle_name": "Anonymous",
            "last_name": "Sharma",
            "email": "abe@gmail.com",
            "mail_address": "Brooklyn, NY USA",
            "occupation": "Geek",
            "phone_number": '+12125552368',
            "input_password": "Abe@1234",
            "confirm_password": "Abe@1234",
        }

    def test_valid_register(self):
        url = reverse("user:register_user")
        response = self.client.get(url)
        self.assertTrue(response.status_code, 200)
        response = self.client.post(url, self.user)
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(User.objects.get(username=self.user["username"]))
        # test invalid register for same username
        response = self.client.post(url, self.user)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(User.objects.count(), 1)

    def test_invalid_register(self):
        self.invalid_user = self.user.copy()
        self.invalid_user["username"] = "ABESHEK"
        self.invalid_user["email"] = "a.com"
        url = reverse("user:register_user")
        response = self.client.post(url, self.invalid_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username=self.invalid_user["username"]).count(), 0)

    def tearDown(self):
        User.objects.all().delete()


class RegisterFormTest(TestCase):
    def setUp(self) -> None:
        self.data = {
            "username": "abeshek",
            "first_name": "Abhishek",
            "middle_name": "Anonymous",
            "last_name": "Sharma",
            "email": "abe@gmail.com",
            "mail_address": "Brooklyn, NY USA",
            "occupation": "Geek",
            "phone_number": '+12125552368',
            "input_password": "Abe@1234",
            "confirm_password": "Abe@1234",
        }

    def test_valid_register_form(self):
        form = RegisterForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_register_invalid_password(self):
        self.invalid_password_data = self.data.copy()
        self.invalid_password_data["input_password"] = "abe1234"
        self.invalid_password_data["confirm_password"] = "abe1234"
        form = RegisterForm(data=self.invalid_password_data)
        self.assertFalse(form.is_valid())
        self.assertFalse("input_password" in form.cleaned_data)

    def test_register_mismatch_password(self):
        self.invalid_password_data = self.data.copy()
        self.invalid_password_data["input_password"] = "Abe@1234"
        self.invalid_password_data["confirm_password"] = "abe@1234"
        form = RegisterForm(data=self.invalid_password_data)
        self.assertFalse(form.is_valid())
        self.assertFalse("confirm_password" in form.cleaned_data)


class LoginFormTest(TestCase):
    def setUp(self) -> None:
        self.data = {
            "username": "abeshek",
            "password": "Abe@1234"
        }

    def test_valid_login_form(self):
        form = LoginForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_invalid_login_form(self):
        self.invalid_data = self.data.copy()
        self.invalid_data["password"] = ""
        form = LoginForm(data=self.invalid_data)
        self.assertFalse(form.is_valid())


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(**{
            "username": "abeshek",
            "first_name": "Abhishek",
            "middle_name": "Anonymous",
            "last_name": "Sharma",
            "email": "abe@gmail.com",
            "mail_address": "Brooklyn, NY USA",
            "occupation": "Geek",
            "phone_number": '+12125552368',
            "password": make_password("Abe@1234"),
        })

    def test_valid_login(self):
        data = {"username": "abeshek", "password": "Abe@1234"}
        url = reverse("user:login_user")
        response = self.client.get(url)
        self.assertTrue(response, 200)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(User.objects.get(username="abeshek"))
        # test session redirection from login to dashboard
        response = self.client.get(url)
        self.assertEqual(response.url, reverse("classifier:overview"))
        self.assertEqual(response.status_code, 302)

    def test_invalid_login(self):
        data = {"username": "abeshek", "password": "abe@1234"}
        url = reverse("user:login_user")
        # test invalid password
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("login_error" in response.context)
        self.assertIsNotNone(User.objects.get(username="abeshek"))
        # test invalid username
        data["username"] = "AbeShek"
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("login_error" in response.context)

    def tearDown(self):
        self.user.delete()


class ChangePasswordFormTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(**{
            "username": "abeshek",
            "first_name": "Abhishek",
            "middle_name": "Anonymous",
            "last_name": "Sharma",
            "email": "abe@gmail.com",
            "mail_address": "Brooklyn, NY USA",
            "occupation": "Geek",
            "phone_number": '+12125552368',
            "password": make_password("Abe@1234"),
        })
        self.data = {
            "current_password": "Abe@1234",
            "input_password": "aBe@1234",
            "confirm_password": "aBe@1234"
        }

    def test_valid_change_password_form(self):
        # user must login to change password
        form = ChangePasswordForm(data=self.data)
        self.assertFalse(form.is_valid())
        # must be a valid user
        self.data["username"] = "ABESHEK"
        form = ChangePasswordForm(data=self.data)
        self.assertFalse(form.is_valid())
        # proper user
        self.data["username"] = "abeshek"
        form = ChangePasswordForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_change_password_current_invalid_password(self):
        self.invalid_password_data = self.data.copy()
        self.invalid_password_data["current_password"] = "abe1234"
        form = ChangePasswordForm(data=self.invalid_password_data)
        self.assertFalse(form.is_valid())
        self.assertFalse("current_password" in form.cleaned_data)

    def test_change_password_invalid_password(self):
        self.invalid_password_data = self.data.copy()
        self.invalid_password_data["input_password"] = "abe1234"
        self.invalid_password_data["confirm_password"] = "abe1234"
        form = ChangePasswordForm(data=self.invalid_password_data)
        self.assertFalse(form.is_valid())
        self.assertFalse("input_password" in form.cleaned_data)

    def test_change_password_mismatch_password(self):
        self.invalid_password_data = self.data.copy()
        self.invalid_password_data["input_password"] = "Abe@1234"
        self.invalid_password_data["confirm_password"] = "abe@1234"
        form = ChangePasswordForm(data=self.invalid_password_data)
        self.assertFalse(form.is_valid())
        self.assertFalse("confirm_password" in form.cleaned_data)
