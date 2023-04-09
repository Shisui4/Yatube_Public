from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls,):
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
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def test_urls_uses_correct_template(self):
        """Тестирование используемых шаблонов по адресам."""
        template_url_used = {
            '/': 'posts/index.html',
            '/group/test/': 'posts/group_list.html',
            '/profile/noname/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html',
        }
        for address, template in template_url_used.items():
            with self.subTest(address=address):
                response = self.authorized.get(address)
                self.assertTemplateUsed(response, template, f'Использован неправильный шаблон в тесте {template} ')

    def test_urls_status_code(self):
        """Тестирование доступа к страницам проекта у пользователей."""
        address_rules = {
            '/': self.guest,
            '/group/test/': self.guest,
            '/profile/noname/': self.guest,
            '/posts/1/': self.guest,
        }
        for address, client in address_rules.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Нет доступа к странице {address} у {client}')
        response = self.authorized.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         f'Нет доступа к странице {response} у {self.authorized}')
        response = self.authorized.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         f'Нет доступа к странице {response} у {self.authorized}')

