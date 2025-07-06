from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import uuid
from groups.models import Group


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None  # username 필드 제거
    name = models.CharField()
    email = models.EmailField(unique=True)

    clean_sense = models.IntegerField(
        default=50, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    clean_type = models.IntegerField(blank=True, null=True)
    profile = models.IntegerField(default=0)
    evaluation_status = models.BooleanField(default=False)
    clean_type_created_at = models.DateTimeField(blank=True, null=True)

    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, related_name="members", blank=True, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.name})"
