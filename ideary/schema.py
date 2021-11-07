import graphene

import ideas.schema
import profiles.schema


class Query(profiles.schema.Query, ideas.schema.Query, graphene.ObjectType):
    pass


class Mutation(profiles.schema.Mutation, ideas.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
