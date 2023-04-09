from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = 'Группа не выбрана'

    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Изображение',
        }
        help_texts = {
            'text': 'Текст поста',
            'group': 'Выберете группу, к которой будет относиться пост',
            'image': 'Прикрепите изображение'
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text) < 5:
            self.add_error('text', 'Текст меньше 5 символов')
        return text


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].empty_label = 'Написать комментарий...'

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Введите комментарий',
        }

