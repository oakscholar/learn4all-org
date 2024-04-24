from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# Create your models here.
class CustomUser(AbstractUser):
    class Meta:
        # This is required to point to the custom user model
        db_table = 'custom_user'

    # Fix the reverse accessor clash by setting a unique related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField()
    interview_type = models.CharField(max_length=100)  # E.g., "Technical", "Behavioral"

    def __str__(self):
        return f"Interview on {self.date.strftime('%Y-%m-%d')} for {self.user.username}"


    def get_full_name(self) -> str:
        return self.first_name + self.last_name


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
