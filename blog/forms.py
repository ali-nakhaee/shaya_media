""" blog.forms file """

from django import forms

from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'published_date')
        labels = {'title': 'عنوان',
                  'text': 'متن',
                  'published_date': 'تاریخ انتشار'}
        