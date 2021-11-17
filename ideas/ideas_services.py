from .models import Idea


def get_visible_ideas(ideas_profile, consulting_profile=None):
    """
    Returns a queryset of all the visible ideas of ideas_profile (Profile) by
    another consulting_profile (Profile). If no consulting_profile is provided
    then it will only return the PUBLIC ones
    """
    visibilities_accepted = [Idea.PUBLIC]
    if consulting_profile:
        if consulting_profile in ideas_profile.get_followers():
            visibilities_accepted.append(Idea.PROTECTED)
        if consulting_profile == ideas_profile:
            # Same case as "my_ideas". Weird, but can happen.
            visibilities_accepted.append(Idea.PRIVATE)

    return Idea.objects.filter(
        profile=ideas_profile, visibility__in=visibilities_accepted
    ).order_by("-created")
