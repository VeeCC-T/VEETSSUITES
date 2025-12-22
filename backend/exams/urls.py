from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, ExamAttemptViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'attempts', ExamAttemptViewSet, basename='examattempt')

app_name = 'exams'

urlpatterns = [
    path('', include(router.urls)),
]