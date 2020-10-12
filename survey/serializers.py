from .models import *
from rest_framework import serializers


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = "__all__"


class SurveyQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestions
        fields = "__all__"


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswers
        fields = "__all__"
