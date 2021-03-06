from graphql.error.base import GraphQLError


def check_user_logged(user) -> bool:
    """
    Check if the User of a request is logged in
    """
    if user.is_anonymous:
        raise GraphQLError("You are not logged in. Login is required for this action.")
    return True


def check_permission_user_idea(user, idea) -> bool:
    """
    Check if the User has permissions over an Idea.
    Initially a user will have permissions over an idea if the user is its owner
    """
    if not idea.profile.user == user:
        raise GraphQLError("You have not permissions to edit/delete this idea")
    return True


def check_permission_user_followrequest(
    user, followrequest, action="accept/deny"
) -> bool:
    """
    Check if the User has permissions over a FollowRequest.
    Initially a user will have permissions over a FollowRequest if the user is the requested Profile
    """
    if not followrequest.requested.user == user:
        raise GraphQLError(f"You have not permissions to {action} this Follow Request")
    return True
