from django.urls import path
from .views import *

urlpatterns = [path("createUser/", createUser.as_view()),
               path("createSurvey/", CreateSurvey.as_view()),
               path("takeSurvey/", TakeSurvey.as_view()),
               path("storeResponses/", StoreResponses.as_view()),
               path("displayResults/", ShowResults.as_view()),
               path("generateThumbnail/", CreateThumbNail.as_view())
               ]
