from django.contrib.auth.models import AbstractUser
from django.db import models

from .settings import (EMAIL_MAX_LENGHT, NAME_MAX_LENGHT)


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=NAME_MAX_LENGHT,
        unique=True,
        db_index=True,
    )
    email = models.EmailField('Почта', max_length=EMAIL_MAX_LENGHT, unique=True)
    first_name = models.CharField('Имя', max_length=NAME_MAX_LENGHT)
    last_name = models.CharField('Фамилия', max_length=NAME_MAX_LENGHT)
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')

    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор постов')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['following', 'user'],
                name='unique_following_user'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на: {self.following}'
