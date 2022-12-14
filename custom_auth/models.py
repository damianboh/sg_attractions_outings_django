from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

# custom user manager to use email to log in instead of username
class CustomUserManager(UserManager): 
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

# custom user, username is now None and 
# email is now unique and required as it is used to log in
class User(AbstractUser): 
    username = None
    email = models.EmailField(
        _("email address"),
        unique=True,
    )

    name = models.CharField(max_length=200, blank=False, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email" # automatically required as it is needed for log in
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, blank=False, null=True)
    email = models.EmailField(_("email address"), primary_key=True, unique=True)
    about = models.TextField(blank=True, null=True) # additional field
 
    def __str__(self):
        return str(self.user.name)