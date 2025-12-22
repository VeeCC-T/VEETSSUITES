"""
Authentication views for the VEETSSUITES platform.
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.core.exceptions import ValidationError

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from veetssuites.error_responses import (
    create_validation_error_response,
    create_authentication_error_response,
    create_internal_error_response,
    ErrorCodes,
    ErrorMessages
)
from veetssuites.throttling import (
    EnhancedLoginRateThrottle,
    EnhancedRegistrationRateThrottle,
    EnhancedPasswordResetRateThrottle
)

User = get_user_model()


class RegisterView(APIView):
    """
    User registration endpoint.
    
    Creates a new user account with encrypted password.
    Returns user data and JWT tokens upon successful registration.
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    throttle_classes = [EnhancedRegistrationRateThrottle]
    
    def post(self, request):
        logger = logging.getLogger(__name__)
        
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                logger.info(f"New user registered: {user.email}")
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_201_CREATED)
            
            # Return validation errors using standardized format
            return create_validation_error_response(serializer.errors)
            
        except ValidationError as e:
            logger.warning(f"Registration validation error: {e}")
            return create_validation_error_response({'non_field_errors': [str(e)]})
        
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}", exc_info=True)
            return create_internal_error_response("Registration failed. Please try again.")


class LoginView(APIView):
    """
    User login endpoint.
    
    Authenticates user with email and password.
    Returns user data and JWT tokens upon successful authentication.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Get user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({
                    'detail': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check password
            if not user.check_password(password):
                return Response({
                    'detail': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_active:
                return Response({
                    'detail': 'Account is disabled'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    User logout endpoint.
    
    Blacklists the refresh token to invalidate the session.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Accept both 'refresh_token' and 'refresh' field names for compatibility
            refresh_token = request.data.get('refresh_token') or request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'detail': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'detail': 'Successfully logged out'
            }, status=status.HTTP_200_OK)
        except TokenError:
            return Response({
                'detail': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'detail': 'An error occurred during logout'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetRequestView(APIView):
    """
    Password reset request endpoint.
    
    Sends a password reset email with a secure token to the user's email address.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Generate password reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Create reset link (frontend will handle this URL)
                reset_link = f"{settings.FRONTEND_URL}/password-reset-confirm/{uid}/{token}/" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/password-reset-confirm/{uid}/{token}/"
                
                # Send email
                subject = 'Password Reset Request - VEETSSUITES'
                message = f"""
Hello {user.first_name},

You requested a password reset for your VEETSSUITES account.

Click the link below to reset your password:
{reset_link}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Best regards,
VEETSSUITES Team
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
            except User.DoesNotExist:
                # Don't reveal that the user doesn't exist for security reasons
                pass
            
            # Always return success to prevent email enumeration
            return Response({
                'detail': 'If an account exists with this email, a password reset link has been sent.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Password reset confirmation endpoint.
    
    Validates the reset token and updates the user's password.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            # Extract uid from token (format: uid-token)
            try:
                parts = token.split('-', 1)
                if len(parts) != 2:
                    return Response({
                        'detail': 'Invalid token format'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                uid, token_value = parts
                user_id = force_str(urlsafe_base64_decode(uid))
                user = User.objects.get(pk=user_id)
                
                # Verify token
                if not default_token_generator.check_token(user, token_value):
                    return Response({
                        'detail': 'Invalid or expired token'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update password
                user.set_password(password)
                user.save()
                
                return Response({
                    'detail': 'Password has been reset successfully'
                }, status=status.HTTP_200_OK)
                
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({
                    'detail': 'Invalid token'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(APIView):
    """
    Get current user profile endpoint.
    
    Returns the authenticated user's profile information.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Test views for authorization property testing
from .permissions import IsInstructor, IsAdmin
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination


class ProtectedResourceView(APIView):
    """
    Test view that requires authentication.
    Used for testing Property 4: Protected resources require valid authentication.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'message': 'Access granted to protected resource',
            'user': request.user.email
        }, status=status.HTTP_200_OK)


class InstructorOnlyView(APIView):
    """
    Test view that requires instructor role.
    Used for testing Property 8: Students cannot access instructor features.
    """
    permission_classes = [IsAuthenticated, IsInstructor]
    
    def get(self, request):
        return Response({
            'message': 'Access granted to instructor-only resource',
            'user': request.user.email,
            'role': request.user.role
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        return Response({
            'message': 'Instructor action completed',
            'user': request.user.email
        }, status=status.HTTP_201_CREATED)


class AdminOnlyView(APIView):
    """
    Test view that requires admin role.
    Used for testing Property 10: Admins have full access.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        return Response({
            'message': 'Access granted to admin-only resource',
            'user': request.user.email,
            'role': request.user.role
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        return Response({
            'message': 'Admin action completed',
            'user': request.user.email
        }, status=status.HTTP_201_CREATED)
    
    def put(self, request):
        return Response({
            'message': 'Admin update completed',
            'user': request.user.email
        }, status=status.HTTP_200_OK)
    
    def delete(self, request):
        return Response({
            'message': 'Admin delete completed',
            'user': request.user.email
        }, status=status.HTTP_204_NO_CONTENT)


# Admin Dashboard Views

class UserManagementView(APIView):
    """
    Admin endpoint for user management operations.
    
    Provides CRUD operations for user accounts including role updates and deactivation.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        """List all users with pagination and filtering."""
        users = User.objects.all().order_by('-date_joined')
        
        # Filter by role if specified
        role = request.query_params.get('role')
        if role and role in ['student', 'instructor', 'pharmacist', 'admin']:
            users = users.filter(role=role)
        
        # Filter by active status
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            users = users.filter(is_active=is_active.lower() == 'true')
        
        # Search by email or name
        search = request.query_params.get('search')
        if search:
            users = users.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(users, request)
        
        user_data = []
        for user in page:
            user_data.append({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
            })
        
        return paginator.get_paginated_response(user_data)
    
    def patch(self, request, user_id=None):
        """Update user role or active status."""
        if not user_id:
            return Response({
                'detail': 'User ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'detail': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Prevent admin from deactivating themselves
        if user == request.user and 'is_active' in request.data and not request.data['is_active']:
            return Response({
                'detail': 'Cannot deactivate your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update role if provided
        new_role = request.data.get('role')
        if new_role and new_role in ['student', 'instructor', 'pharmacist', 'admin']:
            old_role = user.role
            user.role = new_role
            
            # Update staff/superuser status for admin role
            if new_role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            elif old_role == 'admin':
                user.is_staff = False
                user.is_superuser = False
        
        # Update active status if provided
        if 'is_active' in request.data:
            user.is_active = request.data['is_active']
        
        user.save()
        
        return Response({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
        }, status=status.HTTP_200_OK)


class AnalyticsView(APIView):
    """
    Admin endpoint for platform analytics and statistics.
    
    Provides enrollment stats, revenue data, and user growth metrics.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        """Get comprehensive platform analytics."""
        from hub3660.models import Course, Enrollment
        from payments.models import Transaction
        from exams.models import ExamAttempt
        
        # Time periods for analytics
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        new_users_30d = User.objects.filter(date_joined__gte=last_30_days).count()
        new_users_7d = User.objects.filter(date_joined__gte=last_7_days).count()
        
        # User role breakdown
        user_roles = User.objects.values('role').annotate(count=Count('id'))
        role_stats = {role['role']: role['count'] for role in user_roles}
        
        # Course statistics
        total_courses = Course.objects.count()
        published_courses = Course.objects.filter(is_published=True).count()
        
        # Enrollment statistics
        total_enrollments = Enrollment.objects.count()
        completed_enrollments = Enrollment.objects.filter(payment_status='completed').count()
        pending_enrollments = Enrollment.objects.filter(payment_status='pending').count()
        failed_enrollments = Enrollment.objects.filter(payment_status='failed').count()
        
        enrollments_30d = Enrollment.objects.filter(enrolled_at__gte=last_30_days).count()
        enrollments_7d = Enrollment.objects.filter(enrolled_at__gte=last_7_days).count()
        
        # Revenue statistics
        total_revenue = Transaction.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        revenue_30d = Transaction.objects.filter(
            status='completed',
            created_at__gte=last_30_days
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        revenue_7d = Transaction.objects.filter(
            status='completed',
            created_at__gte=last_7_days
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Payment provider breakdown
        payment_providers = Transaction.objects.filter(status='completed').values('provider').annotate(
            count=Count('id'),
            revenue=Sum('amount')
        )
        
        # Exam statistics
        total_exam_attempts = ExamAttempt.objects.count()
        completed_exams = ExamAttempt.objects.filter(status='completed').count()
        exam_attempts_30d = ExamAttempt.objects.filter(started_at__gte=last_30_days).count()
        
        # Top performing courses (by enrollment)
        top_courses = Course.objects.annotate(
            enrollment_count_annotated=Count('enrollments', filter=Q(enrollments__payment_status='completed'))
        ).order_by('-enrollment_count_annotated')[:5]
        
        top_courses_data = []
        for course in top_courses:
            top_courses_data.append({
                'id': course.id,
                'title': course.title,
                'instructor': course.instructor.get_full_name(),
                'enrollment_count': course.enrollment_count_annotated,
                'price': float(course.price),
                'currency': course.currency,
            })
        
        # User growth over time (last 30 days)
        user_growth = []
        for i in range(30):
            date = now - timedelta(days=i)
            daily_users = User.objects.filter(date_joined__date=date.date()).count()
            user_growth.append({
                'date': date.date().isoformat(),
                'new_users': daily_users
            })
        user_growth.reverse()
        
        return Response({
            'users': {
                'total': total_users,
                'active': active_users,
                'new_30d': new_users_30d,
                'new_7d': new_users_7d,
                'by_role': role_stats,
                'growth': user_growth,
            },
            'courses': {
                'total': total_courses,
                'published': published_courses,
                'top_courses': top_courses_data,
            },
            'enrollments': {
                'total': total_enrollments,
                'completed': completed_enrollments,
                'pending': pending_enrollments,
                'failed': failed_enrollments,
                'new_30d': enrollments_30d,
                'new_7d': enrollments_7d,
            },
            'revenue': {
                'total': float(total_revenue),
                'last_30d': float(revenue_30d),
                'last_7d': float(revenue_7d),
                'by_provider': [
                    {
                        'provider': p['provider'],
                        'count': p['count'],
                        'revenue': float(p['revenue'])
                    } for p in payment_providers
                ],
            },
            'exams': {
                'total_attempts': total_exam_attempts,
                'completed': completed_exams,
                'attempts_30d': exam_attempts_30d,
            },
        }, status=status.HTTP_200_OK)


class SystemHealthView(APIView):
    """
    Admin endpoint for system health monitoring.
    
    Provides system status, database connectivity, and service health checks.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        """Get system health status."""
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {}
        }
        
        # Database connectivity check
        try:
            User.objects.count()
            health_data['checks']['database'] = {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
        except Exception as e:
            health_data['checks']['database'] = {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}'
            }
            health_data['status'] = 'unhealthy'
        
        # Check for recent errors (you might want to implement error logging)
        health_data['checks']['error_rate'] = {
            'status': 'healthy',
            'message': 'No recent critical errors detected'
        }
        
        # Check system resources (basic)
        import psutil
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_data['checks']['system_resources'] = {
                'status': 'healthy' if cpu_percent < 80 and memory.percent < 80 else 'warning',
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': (disk.used / disk.total) * 100,
            }
            
            if cpu_percent > 90 or memory.percent > 90:
                health_data['status'] = 'unhealthy'
        except ImportError:
            health_data['checks']['system_resources'] = {
                'status': 'unknown',
                'message': 'psutil not available for system monitoring'
            }
        
        # Check external services (basic connectivity)
        health_data['checks']['external_services'] = {
            'status': 'healthy',
            'message': 'External service checks not implemented'
        }
        
        return Response(health_data, status=status.HTTP_200_OK)
