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

    def get_my_ideas(self):
        """
        Returns a queryset of all the ideas of a Profile ordered by descending date
        """
        return self.idea_set.all().order_by("-created")

    def get_my_followrequests(self):
        """
        Returns a queryset with all the PENDING FollowRequest a Profile have received
        """
        return FollowRequest.objects.filter(
            requested=self, status=FollowRequest.PENDING
        )


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
        """
        Approves a FollowRequest, adding the requestor profile to the followers list of
        the requested profile
        """
        self.status = self.APPROVED
        self.save()
        self.requested.followers.add(self.requestor)

    def reject(self):
        """
        Rejects a FollowRequest, setting its status to REJECTED
        """
        self.status = self.REJECTED
        self.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Post save signal to automatically create the asociated Profile to a User when it's
    created
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Post save signal to automatically update the asociated Profile to a User when it's
    updated
    """
    instance.profile.save()
