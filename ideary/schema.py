import graphene
import graphql_jwt

import ideas.schema
import profiles.schema


class Query(profiles.schema.Query, ideas.schema.Query, graphene.ObjectType):
    pass


class Mutation(profiles.schema.Mutation, ideas.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
