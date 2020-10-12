from inspect import FullArgSpec
from graphene import Field, Int
from graphene import Argument
import graphene
from graphene_django import DjangoObjectType, DjangoListField
from .models import *


class SurveyType(DjangoObjectType):
    class Meta:
        model = Survey


class SurveyQuestionType(DjangoObjectType):
    class Meta:
        model = SurveyQuestions


class UserResponseType(DjangoObjectType):
    class Meta:
        model = UserAnswers


class Query(object):
    surveys = DjangoListField(SurveyType)
    questions = DjangoListField(SurveyQuestionType)
    userResponses = DjangoListField(UserResponseType)
    survey = Field(SurveyType, surveyId=Int())

    def resolve_survey(self, info, surveyId):
        if surveyId:
            return Survey.objects.filter(pk=surveyId).first()
        return None


class CreateSurvey(graphene.Mutation):
    class Arguments:
        surveyName = graphene.String()
        creator_id = graphene.Int()
    survey = graphene.Field(SurveyType)

    def mutate(self, info, surveyName, creator_id=None):

        survey = Survey.objects.create(
            surveyName=surveyName,
            creator=creator_id
        )
        survey.save()
        return CreateSurvey(
            survey=survey
        )


class CreateQuestions(graphene.Mutation):
    class Arguments:
        question = graphene.List(graphene.String)
        surveyId_id = graphene.Int()
        trueCount = graphene.Int()
        falseCount = graphene.Int()
    questions = graphene.List(SurveyQuestionType)
    def mutate(self, info, question, surveyId_id=None, trueCount=None, falseCount=None):

        for ques in question:
            questions = SurveyQuestions.objects.create(
                question=ques,
                surveyId_id=surveyId_id,
                trueCount=trueCount,
                falseCount=falseCount
            )
            questions.save()
        questions = SurveyQuestions.objects.filter(
            surveyId=surveyId_id)
        return CreateQuestions(
            questions=questions
        )


class Mutation(graphene.ObjectType):
    create_survey = CreateSurvey.Field()
    create_question = CreateQuestions.Field()
