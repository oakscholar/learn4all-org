from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone


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
    date = models.DateTimeField(default=timezone.now)
    interview_type = models.CharField(max_length=100)  # E.g., "Technical", "Behavioral"
    goal = models.TextField(blank=True, null=True) 
    skill = models.CharField(blank=True, null=True, max_length=255)
    learning_style = models.CharField(blank=True, null=True, max_length=100)
    learning_wks = models.IntegerField(blank=True, null=True)
    learning_hrs_per_wk = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)


    def __str__(self):
        return f"Interview on {self.date.strftime('%Y-%m-%d')} for {self.user.username}"


    def get_full_name(self) -> str:
        return self.first_name + self.last_name


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


class LearningResult(models.Model):
    profile = models.OneToOneField('Profile', on_delete=models.CASCADE, related_name='learning_result')
    general_wk_result = models.JSONField()
    detail_result = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Learning Result for {self.profile.user.username}"
