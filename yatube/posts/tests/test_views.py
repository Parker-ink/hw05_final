import random
import tempfile
import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms
from faker import Faker
from django.conf import settings
from django.core.cache import cache

from posts.models import Group, Post, Follow

fake = Faker()
User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='Witcher3')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='group-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=fake.text(),
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_group_list_correct_context(self):
        """Шаблон group_list с корректным контекстом"""
        response = self.guest_client.get(reverse('posts:group_list',
                                                 kwargs={'slug':
                                                         self.group.slug}))
        first_object = response.context['page_obj'][0]
        second_object = response.context['group']
        post_image = Post.objects.first().image
        self.assertEqual(post_image, 'posts/small.gif')
        self.assertIn('page_obj', response.context)
        self.assertIn('group', response.context)
        self.assertEqual(first_object, Post.objects.first())
        self.assertEqual(second_object, Group.objects.first())

    def test_post_detail_correct_context(self):
        """Шаблон post_detail с корректным контекстом"""
        reverse_page = reverse('posts:post_detail',
                               kwargs={'post_id': self.post.id})
        response = self.authorized_client.get(reverse_page)
        first_object = response.context['user_post']
        post_image = Post.objects.first().image
        self.assertEqual(post_image, 'posts/small.gif')
        self.assertIn('user_post', response.context)
        self.assertEqual(first_object, Post.objects.first())

    def test_index_correct_context(self):
        """Шаблон index с корректным контекстом"""
        response = self.guest_client.get(reverse('posts:index'))
        test_post = response.context['page_obj'][0]
        post_image = Post.objects.first().image
        self.assertEqual(post_image, 'posts/small.gif')
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.group, self.post.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile с корректным контекстом."""
        response = self.guest_client.get(reverse('posts:profile',
                                                 kwargs={'username':
                                                         self.user.username}))
        test_post = response.context['page_obj'][0]
        post_image = Post.objects.first().image
        self.assertEqual(post_image, 'posts/small.gif')
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.group, self.post.group)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post с корректным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон edit_post с корректным контекстом."""
        self.author_client = Client()
        self.author_client.force_login(self.user)
        response = self.author_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, forms.fields.CharField)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Geralt',
                                            email='Novigrad@mail.ru',
                                            password='Stryga',)
        cls.group = Group.objects.create(
            title='Заголовок для тестовой группы',
            slug='test_slug2',
            description='Тестовое описание')
        cls.post_test_count = random.randint(11, 20)
        cls.post = []
        for i in range(cls.post_test_count):
            cls.post.append(Post(
                author=cls.user,
                text=fake.text(),
                group=cls.group,
            ))
        Post.objects.bulk_create(cls.post)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        """Тестирование паджинатора"""
        all_count = self.post_test_count
        count_one_page = settings.POST_PER_PAGE
        count_two_page = all_count - count_one_page
        tested_urls_paginations = {
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user})
        }
        for url in tested_urls_paginations:
            with self.subTest(url=url):
                response_one_page = self.client.get(url + '?page=1')
                self.assertEqual(
                    len(response_one_page.context['page_obj']),
                    count_one_page)
                response_two_page = self.client.get(url + '?page=2')
                self.assertEqual(
                    len(response_two_page.context['page_obj']),
                    count_two_page)


class CacheTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user(username='Geralt',
                                            email='Novigrad@mail.ru',
                                            password='Stryga',)
        cls.post = Post.objects.create(
            author=cls.user,
            text=fake.text(),
            id=1,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.user = User.objects.create_user(username='Witcher3')
        self.guest_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        """Тест кэширования главной страницы"""
        first_request = self.authorized_client.get(reverse('posts:index'))
        post_1 = Post.objects.get(pk=1)
        post_1.text = 'Мы изменили текст, без обид'
        post_1.save()
        second_request = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(first_request.content, second_request.content)
        cache.clear()
        third_request = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_request.content, third_request.content)


class FollowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user(username='user')

    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(
            username='Geralt',
            email='Novigrad@mail.ru',
            password='Stryga',
        )
        self.user_following = User.objects.create_user(
            username='following',
            email='following@mail.ru',
            password='test'
        )
        self.post = Post.objects.create(
            author=self.user_following,
            text=fake.text()
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)
        self.user_no_author = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_follow(self):
        """Авторизованный
        Пользователь может подписываться на других пользователей.
        """
        self.client_auth_follower.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_following.username}))
        follow_exist = Follow.objects.filter(user=self.user_follower,
                                             author=self.user_following
                                             ).exists()
        self.assertTrue(follow_exist)

    def test_unfollow(self):
        """Авторизованный
        Пользователь может отписываться от других пользователей.
        """
        self.client_auth_follower.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_following.username}))
        self.client_auth_follower.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_following.username}))
        follow_exist = Follow.objects.filter(user=self.user_following,
                                             author=self.user_follower
                                             ).exists()
        self.assertFalse(follow_exist)

    def test_subscription_feed(self):
        """Запись появляется в ленте подписчиков."""
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.client_auth_follower.get('/follow/')
        self.assertIn('page_obj', response.context)
        post_text = response.context["page_obj"][0].text
        self.assertEqual(post_text, self.post.text)

    def test_subscription_feed_not_follow(self):
        """Запись не появляется в ленте тех, кто не подписан."""
        Follow.objects.create(user=self.user_following,
                              author=self.user_following)
        response = self.client_auth_following.get(
            reverse('posts:follow_index'))
        post_text = response.context["page_obj"][0].text
        self.assertIn('page_obj', response.context)
        self.assertEqual(post_text, self.post.text)

    def test_not_follow_user_user(self):
        """Пользователь не может пописаться сам на себя."""
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}))
        follow_exist = Follow.objects.filter(user=self.user,
                                             author=self.user).exists()
        self.assertFalse(follow_exist)
