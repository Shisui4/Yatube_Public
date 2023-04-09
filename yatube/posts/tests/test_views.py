import time

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class TaskPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')
        cls.guest = Client()
        cls.authorized = Client()
        cls.authorized.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Test-Group'
        )
        cls.group_more = Group.objects.create(
            title='Group2',
            slug='secondtest',
            description='Second Group'
        )
        cls.more_post = [Post.objects.create(text=f'Text{x}',
                                             author=cls.user, group=cls.group_more) and time.sleep(0.01)
                         for x in range(15)]
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def test_namespace_to_template(self):
        """Тестирование что правильно срабатывает namespace->template."""
        templates_page_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'noname'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}): 'posts/post_create.html',
            reverse('posts:post_create',): 'posts/post_create.html',
        }
        for reverse_page, template in templates_page_name.items():
            with self.subTest(template=template):
                response = self.authorized.get(reverse_page)
                self.assertTemplateUsed(response, template,
                                        f'Ошибка при проверке шаблона {template}')

    def test_index_page_context(self):
        """Проверка контекста на главной странице у поста."""
        response = self.authorized.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Тестовый текст', f'Неверная проверка {post_text_0}')
        self.assertEqual(post_author_0, 'noname', f'Неверная проверка {post_author_0}')
        self.assertEqual(post_group_0, 'Тестовая группа', f'Неверная проверка {post_group_0}')

    def test_paginator_in_template(self):
        """Тестируем пагинатор на главной странице."""
        response = self.guest.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.guest.get(reverse('posts:index'), {'page': 2})
        self.assertEqual(len(response.context['page_obj']), 6)
        response = self.guest.get(reverse('posts:group_list',
                                          kwargs={'slug': 'secondtest'}))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.guest.get(reverse('posts:group_list',
                                          kwargs={'slug': 'secondtest'}), {'page': 2})
        self.assertEqual(len(response.context['page_obj']), 5)
        response = self.guest.get(reverse('posts:profile',
                                          kwargs={'username': 'noname'}))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.guest.get(reverse('posts:profile',
                                          kwargs={'username': 'noname'}), {'page': 2})
        self.assertEqual(len(response.context['page_obj']), 6)
