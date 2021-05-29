from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    content = models.TextField(max_length=1000)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='authors')
    likes = models.IntegerField(default=0)

    def serialize(self):
        return {
            'content': self.content,
            'date_posted': self.strftime("%b %d %Y, %I:%M %p"),
            'author': self.author,
            'likes': self.likes
        }
