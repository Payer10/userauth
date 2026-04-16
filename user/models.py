from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin, AbstractUser
from django.utils import timezone
import uuid



class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    # phone_number = models.CharField(max_length=15)
    # phone_country_code = models.CharField(max_length=5)
    # full_name = models.CharField(max_length=255)



    is_terms_service = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=50, default='user')
    created_at = models.DateTimeField(default=timezone.now)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__ (self):
        return self.email


class VarificationCode(models.Model):
    PURPOSE_CHOICES = [
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    secret_key = models.UUIDField(null=True, blank=True)

