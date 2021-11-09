import graphene
from graphene_django import DjangoObjectType
from graphql.error.base import GraphQLError

from profiles.permisision_tools import check_permission_user_idea, check_user_logged

from .models import Idea


class IdeaType(DjangoObjectType):
    class Meta:
        model = Idea


class Query(graphene.ObjectType):
    ideas = graphene.List(IdeaType)
    public_ideas = graphene.List(IdeaType)
    my_ideas = graphene.List(IdeaType)
    timeline = graphene.List(IdeaType)

    def resolve_ideas(self, info, **kwargs):
        """
        List all the visible Ideas
        """
        # TODO(alealvpav): Default queryset should be limited to PUBLIC. Then add the
        # PRIVATE own ideas and the PROTECTED of the following profiles
        return Idea.objects.all()

    def resolve_public_ideas(self, info, **kwargs):
        """
        List the PUBLIC (visibility) Ideas
        This functionality is covered by resolve_ideas but it's here for testing purposes
        """
        return Idea.objects.filter(visibility=Idea.PUBLIC)

    def resolve_my_ideas(self, info, **kwargs):
        """
        List the Ideas published by a user
        """
        user = info.context.user
        check_user_logged(user)
        return user.profile.get_my_ideas()
        return user.profile.idea_set.all()

    def resolve_timeline(self, info, **kwargs):
        """
        List the timeline (Ideas) of a logged User. This means all the ideas of the
        logged user and the PUBLIC and PROTECTED of the Profiles he follows (ordered by descending date).
        - Un usuario puede ver un timeline de ideas compuesto por sus propias ideas y las ideas de los usuarios a los que sigue, teniendo en cuenta la visibilidad de cada idea.
        """
        user = info.context.user
        check_user_logged(user)
        # Own ideas
        own_ideas = user.profile.get_my_ideas()
        # Ideas of the profiles followed by the user
        followed_ideas = Idea.objects.exclude(visibility=Idea.PRIVATE).filter(
            profile__followers=user.profile
        )
        return (own_ideas | followed_ideas).distinct().order_by("-created")


class CreateIdea(graphene.Mutation):
    idea = graphene.Field(IdeaType)

    class Arguments:
        content = graphene.String(required=True)
        visibility = graphene.String(required=False)

    def mutate(self, info, content, **kwargs):
        """
        Creates an idea and optionally sets its visibility to a non-default value.
        - Un usuario puede publicar una idea como un texto corto en cualquier momento.
        - Un usuario puede establecer la visibilidad de una idea en el momento de su creacion o editarla posteriormente.
        """
        user = info.context.user

        check_user_logged(user)

        idea = Idea(profile=user.profile, content=content)
        if "visibility" in kwargs:
            idea.visibility = kwargs["visibility"]
        idea.save()

        return CreateIdea(idea=idea)
    id = graphene.Int()
    profile = graphene.Int()
    content = graphene.String()
    visibility = graphene.String()

    class Arguments:
        profile = graphene.Int()
        content = graphene.String()
        visibility = graphene.String()

    def mutate(self, profile, content, visibility):
        idea = Idea(profile=profile, content=content, visibility=visibility)
        idea.save()

        return CreateIdea(
            id=idea.id,
            profile=idea.profile,
            content=idea.content,
            visibility=idea.visibility,
        )


class Mutation(graphene.ObjectType):
    create_idea = CreateIdea.Field()
