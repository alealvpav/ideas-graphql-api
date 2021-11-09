from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver
from mailing.views import send_new_idea_mail

from profiles.models import Profile


class Idea(models.Model):

    # Visibility options
    PUBLIC = "PUB"  # Public: Everyone can see the idea
    PROTECTED = "PRO"  # Only accepted followers can see the idea
    PRIVATE = "PRI"  # Only the owner can see the idea.
    VISIBILITY_OPTIONS = [
        (PUBLIC, "Public"),
        (PROTECTED, "Protected"),
        (PRIVATE, "Private"),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.CharField(max_length=500, blank=False, null=False)
    visibility = models.CharField(
        max_length=3, choices=VISIBILITY_OPTIONS, default=PUBLIC
    )
    created = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Idea)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Post save signal to notify the followers about the new published idea
    """
    if created and instance.visibility in [Idea.PUBLIC, Idea.PROTECTED]:
        send_new_idea_mail(instance)
