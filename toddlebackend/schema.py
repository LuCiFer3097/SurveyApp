import graphene
import survey.schema


class Query(survey.schema.Query, graphene.ObjectType):
    pass


class Mutation(survey.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
