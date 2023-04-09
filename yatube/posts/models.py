from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

#from pytils.translit import slugify Позволяет транслитом добавлять напр. slug

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Название группы')
    slug = models.SlugField(unique=True,
                            verbose_name='Уникальный адрес')
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    text = models.TextField(verbose_name='Содержимое поста')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор поста')
    group = models.ForeignKey(Group,
                              on_delete=models.CASCADE,
                              blank=True,
                              null=True,
                              related_name='post',
                              verbose_name='Группа')
    image = models.ImageField(verbose_name='Картинка',
                              upload_to='posts/images/',
                              blank=True)
    
    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             verbose_name='Пост для комментария',
                             related_name='comments')
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Поле ввода комментария')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата добавления комментария')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор комментария',
                               related_name='comments')

    class Meta:
        ordering = ('post',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User, verbose_name='Подписчик',
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, verbose_name='Издатель',
                               on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        verbose_name = 'Фалловер'
        verbose_name_plural = 'Фалловеры'
        UniqueConstraint(fields=['user', 'author'],
                         name='uniq_follow_following')

