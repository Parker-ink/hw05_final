from http import HTTPStatus

from django.core.cache import cache
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from faker import Faker

from ..models import Group, Post

User = get_user_model()
fake = Faker()


class PostsURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='VadimSuhov')
        cls.user2 = User.objects.create_user(username='JohnKonstantin')
        cls.group = Group.objects.create(
            slug='group-slug',
            description=fake.text(),
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=fake.text(),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user2)
        cache.clear()

    def test_urls_status_guest(self):
        """Проверека статуса гостя"""
        templates_check_status = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list', kwargs={'slug':
                                                self.group.slug}):
                                                    HTTPStatus.OK,
            reverse('posts:profile', kwargs={'username':
                                             self.user.username}):
                                                 HTTPStatus.OK,
            reverse('posts:post_detail', kwargs={'post_id':
                                                 self.post.id}):
                                                    HTTPStatus.OK,
        }
        for url, status in templates_check_status.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_create_available_authorized_user(self):
        """Авторизованному пользователю доступно создание поста /create/"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_authorized_user_edit(self):
        """Переадресация после /edit/ на страницу просмотра поста"""
        response = self.authorized_client_2.get(reverse('posts:post_edit',
                                                        kwargs={'post_id':
                                                                self.post.id}))
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id':
                                                       self.post.id}))

    def test_edit_available_author(self):
        """Автору доступно редактирование поста /edit/"""
        self.author_client = Client()
        self.author_client.force_login(self.user)
        response = self.author_client.get(reverse('posts:post_edit',
                                                  args=[self.post.id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_template_create(self):
        """Тест соответсвтия шаблона /create/"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_authorized(self):
        """Проверка создания и редактирования постов
        для авторизованного пользователя
        """
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_comment_authorized(self):
        """Комментировать может только авторизованный пользователь"""
        response = self.authorized_client.get(reverse('posts:add_comment',
                                              args=[self.post.id]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_template(self):
        """URL доступные для всех используют нужные шаблоны"""
        urls_template = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=[self.group.slug]): 'posts/group_list.html',
            reverse('posts:profile',
                    args=[self.user]): 'posts/profile.html',
            reverse('posts:post_detail',
                    args=[self.post.id]): 'posts/post_detail.html',
        }
        for url, template in urls_template.items():
            with self.subTest(template=template):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)

    def test_redirect_guests_private_page(self):
        """Страницы для авторизованных пользователей недоступны
         неавторизованным переадресация на страницу входа
        """
        url_posts_edit = reverse('posts:post_edit', args=[self.post.id])
        url_login = reverse('users:login')
        url_create = reverse('posts:post_create')
        url_comments = reverse('posts:add_comment', args=[self.post.id])
        url_redirect = {
            url_posts_edit: f'{url_login}?next={url_posts_edit}',
            url_create: f'{url_login}?next={url_create}',
            url_comments: f'{url_login}?next={url_comments}'
        }
        for url, redirect in url_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)
