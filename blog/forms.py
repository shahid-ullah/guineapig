# blog/forms.py

from django import forms

from .models import Comment, Post, ImageStore

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                            widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class NewPost(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['tags', 'title', 'slug', 'author', 'body', 'publish', 'status',]


class ImageUploadForm(forms.ModelForm):

    class Meta:
        model = ImageStore
        fields = ['title', 'cover']
