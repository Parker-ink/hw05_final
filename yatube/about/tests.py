from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class TaskURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Fatality')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_uses_correct_template(self):
        reverse = self.authorized_client.get('/about/author/')
        self.assertTemplateUsed(reverse, 'about/author.html')

    def test_url_uses_correct_template(self):
        reverse = self.authorized_client.get('/about/tech/')
        self.assertTemplateUsed(reverse, 'about/tech.html')
