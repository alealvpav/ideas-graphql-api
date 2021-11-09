import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql.error.base import GraphQLError

from profiles.permisision_tools import (
    check_permission_user_followrequest,
    check_user_logged,
)

from .models import FollowRequest, Profile, User


class UserType(DjangoObjectType):
    class Meta:
        model = User


class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = {"user__username": ["exact", "icontains", "istartswith"]}
        interfaces = (graphene.relay.Node,)


class FollowRequestType(DjangoObjectType):
    class Meta:
        model = FollowRequest


class Query(graphene.ObjectType):
    profiles = graphene.List(ProfileType)
    searchable_profiles = graphene.relay.Node.Field(ProfileType)
    profiles_search = DjangoFilterConnectionField(ProfileType)
    users = graphene.List(UserType)
    me = graphene.Field(UserType)
    followers = graphene.List(ProfileType)
    following = graphene.List(ProfileType)
    my_follow_requests = graphene.List(FollowRequestType)

    def resolve_profiles(self, info, **kwargs):
        return Profile.objects.all()

    def resolve_users(self, info, **kwargs):
        return User.objects.all()

    def resolve_me(self, info, **kwargs):
        user = info.context.user
        check_user_logged(user)
        return user

    def resolve_followers(self, info, **kwargs):
        """
        Returns the list of Profiles that follow the Profile of the User in the request
        - Un usuario puede ver el listado de gente que le sigue
        """
        user = info.context.user
        check_user_logged(user)
        return user.profile.get_followers()

    def resolve_following(self, info, **kwargs):
        """
        Returns the list of Profiles followed by the Profile of the User in the request
        - Un usuario puede ver el listado de gente a la que sigue
        """
        user = info.context.user
        check_user_logged(user)
        return user.profile.get_following()

    def resolve_my_follow_requests(self, info, **kwargs):
        """
        Returns the list of PENDING FollowRequest received by the logged User Profile
        - Un usuario puede ver el listado de solicitudes de seguimiento recibidas y aprobarlas o denegarlas
        """
        user = info.context.user
        check_user_logged(user)
        return user.profile.get_my_followrequests()


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()

    def mutate(self, info, username, email, password):
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()

        return CreateUser(user=user)


class UpdatePassword(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        password = graphene.String()

    def mutate(self, info, password):
        """
        A logged user can update his password here
        - Un usuario debe poder cambiar su contraseña.
        """
        user = info.context.user
        if check_user_logged(user):
            user.set_password(password)
            user.save()

        return UpdatePassword(user=user)


class CreateFollowRequest(graphene.Mutation):
    followrequest = graphene.Field(FollowRequestType)

    class Arguments:
        requested_id = graphene.Int()

    def mutate(self, info, requested_id, **kwargs):
        """
        Creates a FollowRequest from the logged User Profile (as requestor) to the
        requested Profile
        - Un usuario puede solicitar seguir a otro usuario
        """
        user = info.context.user
        if check_user_logged(user):
            requestor = user.profile
            try:
                requested = Profile.objects.get(pk=requested_id)
            except Profile.DoesNotExist:
                raise GraphQLError("The Profile you're trying to follow does not exist")
            if not FollowRequest.objects.filter(
                requested=requested, requestor=requestor
            ).exists():
                followrequest = FollowRequest(
                    requestor=requestor,
                    requested=requested,
                )
                followrequest.save()
            else:
                raise GraphQLError("It already exists a FollowRequest to that Profile")
            return CreateFollowRequest(followrequest=followrequest)


class AcceptFollowRequest(graphene.Mutation):
    followrequest = graphene.Field(FollowRequestType)

    class Arguments:
        follow_request_id = graphene.Int()

    def mutate(self, info, follow_request_id, **kwargs):
        """
        Accepts a pending FollowRequest to the logged User Profile
        - Un usuario puede ver el listado de solicitudes de seguimiento recibidas y aprobarlas o denegarlas
        """
        user = info.context.user
        if check_user_logged(user):
            requestor = user.profile
            try:
                followrequest = FollowRequest.objects.get(pk=follow_request_id)
            except FollowRequest.DoesNotExist:
                raise GraphQLError(
                    "The Follow Request you're trying to accept does not exist"
                )
            if check_permission_user_followrequest(
                user, followrequest, action="accept"
            ):
                followrequest.approve()

            return AcceptFollowRequest(followrequest=followrequest)


class DenyFollowRequest(graphene.Mutation):
    followrequest = graphene.Field(FollowRequestType)

    class Arguments:
        follow_request_id = graphene.Int()

    def mutate(self, info, follow_request_id, **kwargs):
        """
        Denies a pending FollowRequest to the logged User Profile
        - Un usuario puede ver el listado de solicitudes de seguimiento recibidas y aprobarlas o denegarlas
        """
        user = info.context.user
        if check_user_logged(user):
            requestor = user.profile
            try:
                followrequest = FollowRequest.objects.get(pk=follow_request_id)
            except FollowRequest.DoesNotExist:
                raise GraphQLError(
                    "The Follow Request you're trying to deny does not exist"
                )

            if check_permission_user_followrequest(user, followrequest, action="deny"):
                followrequest.reject()

            return AcceptFollowRequest(followrequest=followrequest)


class StopFollowing(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.Int()

    def mutate(self, info, id, **kwargs):
        """
        Makes a profile to stop following another
        - Un usuario puede dejar de seguir a alguien
        """
        user = info.context.user
        if check_user_logged(user):
            try:
                followed_profile = Profile.objects.get(pk=id)
            except Profile.DoesNotExist:
                raise GraphQLError("The Profile of your request does not exist")
            followed_profile.followers.remove(user.profile)
        return StopFollowing(ok=True)


class DeleteFollower(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.Int()

    def mutate(self, info, id, **kwargs):
        """
        Removes a Profile from the follower Profiles of the logged User
        - Un usuario puede eliminar a otro usuario de su lista de seguidores
        """
        user = info.context.user
        if check_user_logged(user):
            try:
                follower = Profile.objects.get(pk=id)
            except Profile.DoesNotExist:
                raise GraphQLError("The Profile of your request does not exist")
            user.profile.followers.remove(follower)
        return DeleteFollower(ok=True)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_password = UpdatePassword.Field()
    create_follow_request = CreateFollowRequest.Field()
    accept_follow_request = AcceptFollowRequest.Field()
    deny_follow_request = DenyFollowRequest.Field()
    stop_following = StopFollowing.Field()
    delete_follower = DeleteFollower.Field()
