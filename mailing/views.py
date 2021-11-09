from django.shortcuts import render


def send_new_idea_mail(idea):
    """
    This is a mock method that is supposed to send a mail/notification to the followers
    of the profile that published a new idea
    """
    # Get email/notification template
    # Fill with idea.profile and idea.content
    # Send to idea.profile.followers
    pass


def send_restore_password(email):
    """
    This is a mock method that is supposed to send an email with a magic link to
    recover the password
    """
    pass
