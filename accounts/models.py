from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models import OneToOneField


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, username, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        if not username:
            raise ValueError('User must have an username')

        user = self.model(email=self.normalize_email(email), username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """Create and return a new superuser."""
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, related_name='user_profile')
    about = models.TextField(max_length=500, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='users/cover_photos', blank=True, null=True)
    info_font_color = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    state = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


class Subscriber(models.Model):
    email = models.EmailField(unique=True, null=True)
    data_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class NewsletterEmail(models.Model):
    """Model for storing already sent newsletter messages."""
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title


class MessageToStaff(models.Model):
    """Model for storing messages that visitors/ users
       leave at "about us" page."""
    subject = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Messages to staff"
        ordering = ['-date']

    def __str__(self):
        return f'{self.username}: {self.subject}'
