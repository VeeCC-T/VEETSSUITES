"""
HUB3660 URL configuration.
"""

from django.urls import path
from . import views

app_name = 'hub3660'

urlpatterns = [
    # Public course endpoints
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    
    # Course management endpoints (instructor only)
    path('courses/create/', views.CourseCreateView.as_view(), name='course-create'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course-update'),
    path('instructor/courses/', views.InstructorCoursesView.as_view(), name='instructor-courses'),
    
    # Enrollment endpoints
    path('courses/<int:course_id>/enroll/', views.enroll_in_course, name='course-enroll'),
    path('courses/<int:course_id>/enrollment-status/', views.check_enrollment_status, name='enrollment-status'),
    path('student/enrollments/', views.StudentEnrollmentsView.as_view(), name='student-enrollments'),
    
    # Session endpoints
    path('courses/<int:course_id>/sessions/', views.CourseSessionsView.as_view(), name='course-sessions'),
    path('sessions/', views.SessionCreateView.as_view(), name='session-create'),
    path('sessions/<int:session_id>/recording/', views.get_session_recording, name='session-recording'),
    path('sessions/<int:session_id>/register/', views.register_student_for_session, name='session-register'),
    
    # Recording endpoints
    path('courses/<int:course_id>/recordings/', views.get_course_recordings, name='course-recordings'),
    
    # Zoom webhook
    path('zoom/webhook/', views.zoom_webhook, name='zoom-webhook'),
]