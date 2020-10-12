from django.urls import path
from .views import *

urlpatterns = [path("createUser/", createUser.as_view()),
               path("createSurvey/", CreateSurvey.as_view()),
               path("displaySurvey/", DisplaySurvey.as_view()),
               path("takeSurvey/", TakeSurvey.as_view()),
               path("displayResults/", ShowResults.as_view()),

               # BONUS
               path("generateThumbnail/", CreateThumbNail.as_view())
               ]
