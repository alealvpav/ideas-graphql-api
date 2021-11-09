import graphene
from graphene_django import DjangoObjectType
from graphql.error.base import GraphQLError

from profiles.permisision_tools import check_user_logged

from .models import Profile, User


class UserType(DjangoObjectType):
    class Meta:
        model = User


class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile


class Query(graphene.ObjectType):
    profiles = graphene.List(ProfileType)
    users = graphene.List(UserType)
    me = graphene.Field(UserType)
    followers = graphene.List(ProfileType)
    following = graphene.List(ProfileType)

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


# class CreateProfile(graphene.Mutation):
#     pass


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_password = UpdatePassword.Field()
