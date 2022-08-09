from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='user',
            password='HalfLife2',
            email='tests@mail.ru'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.login(
            username='user',
            password='HalfLife2'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес соответствует заданному шаблону."""
        templates_url_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_change_form'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }

        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_user.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_exist_guest_user(self):
        """Доступ к страницам. Неавторизованный пользователь."""
        status_code_url = {
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:password_reset_form'): HTTPStatus.OK,
            reverse('users:password_change_form'): HTTPStatus.FOUND,
            reverse('users:password_change_done'): HTTPStatus.FOUND,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
        }

        for url, status_code in status_code_url.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url).status_code
                self.assertEqual(status_code, response)

    def test_urls_exist_authorized_user(self):
        """Доступ к страницам. Авторизованный пользователь."""
        status_code_url = {
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:password_reset_form'): HTTPStatus.OK,
            reverse('users:password_change_form'): HTTPStatus.OK,
            reverse('users:password_change_done'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
        }

        for url, status_code in status_code_url.items():
            with self.subTest(url=url):
                response = self.authorized_user.get(url).status_code
                self.assertEqual(status_code, response)
