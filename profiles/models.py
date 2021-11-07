from django.db import models
from django.contrib.auth.models import AbstractUser

from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):

    email = models.EmailField(blank=True, unique=True)


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField("self", symmetrical=False, blank=True)

    def __str__(self) -> str:
        return str(self.user)


class FollowRequest(models.Model):

    # Statusses
    PENDING = "PEN"
    APPROVED = "APP"
    REJECTED = "REJ"
    STATUSES = [(PENDING, "Pending"), (APPROVED, "Approved"), (REJECTED, "Rejected")]

    requestor = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="requests",
        related_query_name="request",
    )
    requested = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="pending_requests",
        related_query_name="pending_request",
    )
    status = models.CharField(max_length=3, choices=STATUSES, default=PENDING)

    def approve(self):
        self.status = self.APPROVED
        self.save()

    def reject(self):
        self.status = self.REJECTED
        self.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
