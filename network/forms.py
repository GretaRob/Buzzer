from django.contrib.auth import models
from django.forms import ModelForm, fields
from django import forms
from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['content']
