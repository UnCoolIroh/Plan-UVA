from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from .models import Project_user
from allauth.socialaccount.models import SocialAccount, SocialLogin
@receiver(user_signed_up)
def create_project_user(request, user, **kwargs):
    Project_user.objects.get_or_create(user=user, email=user.email, username=user.username)

