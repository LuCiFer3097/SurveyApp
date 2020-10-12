
from django.db import models
# from django.contrib.auth.models import AbstractBaseUser
# Create your models here.
from django.contrib.auth.models import User
from django.conf import settings


class Created(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Survey(Created):
    surveyId = models.AutoField(primary_key=True)
    surveyName = models.CharField(max_length=50)
    creator = models.ForeignKey(
        User, to_field='username', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.surveyName


class SurveyQuestions(Created):
    questionId = models.AutoField(primary_key=True)
    surveyId = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    trueCount = models.IntegerField(default=0)
    falseCount = models.IntegerField(default=0)

    def __str__(self):
        return self.question


class UserAnswers(Created):
    responseId = models.AutoField(primary_key=True)
    answer = models.BooleanField()
    questionId = models.ForeignKey(SurveyQuestions, on_delete=models.CASCADE)
    user = models.ForeignKey(User, to_field='username',
                             on_delete=models.CASCADE)
    surveyId = models.ForeignKey(
        Survey, on_delete=models.CASCADE)
