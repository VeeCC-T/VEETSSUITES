"""
URL configuration for authentication endpoints.
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

app_name = 'accounts'

urlpatterns = [
    # JWT token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Authentication endpoints (to be implemented in task 3.2)
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
    
    # Test endpoints for authorization property testing
    path('test/protected/', views.ProtectedResourceView.as_view(), name='test_protected'),
    path('test/instructor-only/', views.InstructorOnlyView.as_view(), name='test_instructor_only'),
    path('test/admin-only/', views.AdminOnlyView.as_view(), name='test_admin_only'),
    
    # Admin dashboard endpoints
    path('admin/users/', views.UserManagementView.as_view(), name='admin_users'),
    path('admin/users/<int:user_id>/', views.UserManagementView.as_view(), name='admin_user_detail'),
    path('admin/analytics/', views.AnalyticsView.as_view(), name='admin_analytics'),
    path('admin/health/', views.SystemHealthView.as_view(), name='admin_health'),
]
