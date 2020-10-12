import urllib.request
from PIL import Image
from resizeimage import resizeimage
import boto3
from botocore.exceptions import NoCredentialsError
from .models import *
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
import urllib.request
from PIL import Image
from rest_framework import generics
from rest_framework.mixins import RetrieveModelMixin
from django.contrib.auth.models import User


ACCESS_KEY = 'AKIAZYNKOZNBCA2AVCTK'
SECRET_KEY = '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'


class CustomResponse():
    def successResponse(self, data={}, status=status.HTTP_200_OK, description="SUCCESS"):
        return Response(
            {
                "success": True,
                "errorCode": 0,
                "description": description,
                "info": data
            }, status=status)

    def errorResponse(self, data={}, description="ERROR", errorCode=1, status=status.HTTP_400_BAD_REQUEST):
        return Response(
            {
                "success": False,
                "errorCode": errorCode,
                "description": description,
                "info": data
            }, status=status)


class createUser(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        User.objects.create_user(username, password=password)
        return CustomResponse().successResponse(description="User Created")


class CreateSurvey(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def AddQuestions(self, surveyId, questions):
        for question in questions:
            dic = {
                "surveyId": surveyId,
                "question": question,
            }
            serializers = SurveyQuestionsSerializer(data=dic)
            if serializers.is_valid():
                serializers.save()
            else:
                return CustomResponse().errorResponse(serializers.errors, description="Cannot add question to the survey")

    def post(self, request):
        surveyName = request.data.get("surveyName")
        questions = request.data.get("questions")
        user = request.user.username
        dic = {"surveyName": surveyName, "creator": user}
        serializer = SurveySerializer(data=dic)
        if serializer.is_valid():
            serializer.save()
            surveyObj = serializer.data
            surveyId = surveyObj['surveyId']

            # Adding the question to the survey
            self.AddQuestions(surveyId, questions)

            return CustomResponse().successResponse(serializer.data, description="Created the survey")
        else:
            return CustomResponse().errorResponse(serializer.errors, description="Cannot create the survey")


class TakeSurvey(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        surveyId = request.GET.get("surveyId")
        print(request.user.username)
        surveyObj = SurveyQuestions.objects.filter(surveyId=surveyId)

        if surveyObj:
            survey = []
            for ques in surveyObj:
                dic = {}
                dic = {
                    # Sending questionId for the frontend to store the question and the response which will be used further in displaying the result
                    "questionId": ques.questionId,
                    "question": ques.question,
                    "Option1": "True",
                    "Option2": "False"
                }
                survey.append(dic)
            return CustomResponse().successResponse(survey, description="You can take the survey")
        else:
            return CustomResponse().errorResponse("No such survey present")

# Call this API when the user submit the survey to store the responses


class StoreResponses(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        answers = request.data.get("responses")
        surveyId = request.data.get("surveyId")

        # Checking If the user has already given the survey
        ansObj = UserAnswers.objects.filter(
            surveyId=surveyId, user=request.user.username)
        if ansObj:
            return CustomResponse().errorResponse(description="you have already given the survey")

        for ans in answers:
            quesObj = SurveyQuestions.objects.filter(questionId=ans[0]).first()
            if ans[1].lower() == "true":
                quesObj.trueCount += 1
            elif ans[1].lower() == 'false':
                quesObj.falseCount += 1
            else:
                return CustomResponse().errorResponse(description="The question has only two options True or False")
            quesObj.save()

            dic = {
                "user": request.user.username,
                "surveyId": surveyId,
                "questionId": ans[0],
                "answer": ans[1].lower()
            }
            serializer = UserResponseSerializer(data=dic)
            if serializer.is_valid():
                serializer.save()
            else:
                return CustomResponse().errorResponse(serializer.errors, description="Cannot store the response")
        return CustomResponse().successResponse(description="Stored all the answers")


class ShowResults(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    # Get the summmary for each Question for that survey
    def GetQuestionInsights(self, surveyId):
        questionObj = SurveyQuestions.objects.filter(surveyId=surveyId)
        finalResult = []
        for ques in questionObj:
            result = {}
            totalResponses = ques.trueCount+ques.falseCount
            truePercent = (ques.trueCount/totalResponses)*100
            falsePercent = 100 - truePercent
            result['Question'] = ques.question
            result['TotalResponses'] = totalResponses
            result['NoOfTrue'] = ques.trueCount
            result['TruePercent'] = truePercent
            result['NoOfFalse'] = ques.falseCount
            result['FalsePercent'] = falsePercent
            finalResult.append(result)
        return finalResult

    def GetIndividualInsight(self, surveyId):
        persons = set()
        responsesObj = UserAnswers.objects.filter(surveyId=surveyId)
        print(responsesObj)

        # Storing the users who gave the survey
        for ans in responsesObj:
            persons.add(ans.user.username)

        persons = list(persons)
        noOfpersons = len(persons)
        FInsight = []
        for user in persons:

            # extracting all the responses for the user for that survey
            responsesObj = UserAnswers.objects.filter(
                surveyId=surveyId, user=user)
            Insight = {}
            Insight = {"User": user}
            result = []

            # Iterating through the responses to add them to the result
            for res in responsesObj:
                finalResult = {}
                finalResult['Question'] = res.questionId.question
                finalResult['Response'] = res.answer
                result.append(finalResult)
            Insight["Responses"] = result
            FInsight.append(Insight)

        return FInsight, noOfpersons, persons

    def post(self, request):
        try:
            surveyId = request.data.get("surveyId")
            surveyObj = Survey.objects.filter(surveyId=surveyId).first()

            questionInsight = self.GetQuestionInsights(surveyId)
            individualInsight, totalResponse, Users = self.GetIndividualInsight(
                surveyId)
            finalResult = {"Survey": surveyObj.surveyName,
                           "TotalResponses": totalResponse,
                           "PersonWhoDidTheSurvey": Users,
                           "QuestionInsight": questionInsight,
                           "IndividualInsight": individualInsight}
            return CustomResponse().successResponse(finalResult, description="Displaying the Results")
        except Exception as error:
            return CustomResponse().errorResponse(description="Cannot display the Results")


# BONUS
class CreateThumbNail(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        url_data = request.data.get("url")
        image_name = url_data.split("/")[-1]
        urllib.request.urlretrieve(url_data, 'Images/'+image_name)
        with open('Images/'+image_name, 'r+b') as f:
            with Image.open(f) as image:
                cover = resizeimage.resize_cover(image, [50, 50])
                cover.save("Resized-Images/"+image_name, image.format)
                s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                                  aws_secret_access_key=SECRET_KEY)
                try:
                    s3.upload_file('Resized-Images/'+image_name, 'ccbucket-12345-resized',
                                   image_name, ExtraArgs={'ContentType': 'image/jpeg', 'ACL': 'public-read'})
                    return CustomResponse().successResponse({"resized_url": "https://ccbucket-12345-resized.s3.ap-south-1.amazonaws.com/"+image_name}, description="This is the URL for the resized image.")
                except FileNotFoundError:
                    return CustomResponse().errorResponse(description="file not found/unable to download the image", status=status.HTTP_404_NOT_FOUND)
                except NoCredentialsError:
                    return CustomResponse().errorResponse(description="AWS Credential was not valid")
