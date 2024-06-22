from decimal import Decimal

from django.conf import settings
from django.db.models import (
    Model,
    CharField,
    TextField,
    IntegerField,
    BooleanField,
    DecimalField,
    EmailField,
    ForeignKey,
    ManyToManyField,
    CASCADE,
)
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')

        user: User = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email: str, password: str):
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email: str|EmailField = EmailField(max_length=255, unique=True)
    name: str|CharField = CharField(max_length=255)
    is_active: bool|BooleanField = BooleanField(default=True)
    is_staff: bool|BooleanField = BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(Model):
    name: str|CharField = CharField(max_length=255)
    user: User|ForeignKey = ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=CASCADE)

    def __str__(self) -> str:
        return self.name


class Recipe(Model):
    user: User|ForeignKey = ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=CASCADE)
    title: str|CharField = CharField(max_length=255)
    description: str|TextField = TextField(blank=True)
    time_minutes: int|IntegerField = IntegerField()
    price: Decimal|DecimalField = DecimalField(max_digits=5, decimal_places=2)
    link: str|CharField = CharField(max_length=255, blank=True)
    tags: list[Tag]|ManyToManyField = ManyToManyField(to='Tag')

    def __str__(self) -> str:
        return self.title
