from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):

    USER = 'user'
    ADMIN = 'admin'

    ROLES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Недопустимые символы в поле Имя пользователя'
            ),
        ]
    )
    password = models.CharField(
        max_length=128,
        verbose_name='Пароль',
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    role = models.CharField(
        max_length=16,
        blank=True,
        choices=ROLES,
        default=USER,
        verbose_name='Роль',
    )

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_super_user(self):
        return self.role == self.ADMIN
