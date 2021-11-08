import graphene
from graphene_django import DjangoObjectType

from .models import Idea


class IdeaType(DjangoObjectType):
    class Meta:
        model = Idea


class Query(graphene.ObjectType):
    ideas = graphene.List(IdeaType)

    def resolve_ideas(self, info, **kwargs):
        return Idea.objects.all()

    def resolve_public_ieas(self, info, **kwargs):
        return Idea.objects.filter(visibility=Idea.PUBLIC)

    def resolve_my_ideas(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("User not logged in")
        return user.profile.idea_set.all()


class CreateIdea(graphene.Mutation):
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
