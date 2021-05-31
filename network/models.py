from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    pass


class Post(models.Model):
    content = models.TextField(max_length=1000)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='authors')
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.content


class Follow(models.Model):
    target = models.ForeignKey(
        User, on_delete=CASCADE, related_name='followers')
    follow = models.ForeignKey(User, on_delete=CASCADE, related_name='targets')
