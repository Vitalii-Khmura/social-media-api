import os.path
import uuid

from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from social_media_api import settings


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class GenderChoices(models.TextChoices):
        MALE = "Male",
        Female = "Female"

    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(null=False, max_length=24, unique=True)

    gender = models.CharField(
        max_length=25,
        choices=GenderChoices.choices
    )


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username


class Profile(models.Model):

    class FollowChoices(models.TextChoices):
        Follow = "Follow",
        Unfollow = "Unfollow"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    following = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="followers",
        blank=True
    )

    hobby = models.CharField(null=True, max_length=255)
    profile_image = models.URLField(null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Сигнал, який автоматично створює профіль при створенні користувача.
    """
    if created:
        Profile.objects.create(user=instance)
