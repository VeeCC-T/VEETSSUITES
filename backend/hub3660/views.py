"""
HUB3660 views for course management API endpoints.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
import json
import logging
from accounts.permissions import IsInstructor, IsStudent
from .models import Course, Enrollment, Session
from .serializers import (
    CourseListSerializer, CourseDetailSerializer, CourseCreateUpdateSerializer,
    EnrollmentSerializer, EnrollmentCreateSerializer, SessionSerializer,
    SessionCreateSerializer
)
from .zoom_service import zoom_service
from .storage import recording_storage

logger = logging.getLogger(__name__)


class CourseListView(generics.ListAPIView):
    """
    Public endpoint to list all published courses.
    
    GET /api/hub3660/courses/
    """
    
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Return only published courses."""
        return Course.objects.filter(is_published=True).select_related('instructor')


class CourseDetailView(generics.RetrieveAPIView):
    """
    Public endpoint to get course details.
    
    GET /api/hub3660/courses/{id}/
    """
    
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Return only published courses."""
        return Course.objects.filter(is_published=True).select_related('instructor')


class CourseCreateView(generics.CreateAPIView):
    """
    Instructor-only endpoint to create new courses.
    
    POST /api/hub3660/courses/
    """
    
    serializer_class = CourseCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor]
    
    def perform_create(self, serializer):
        """Set the instructor to the current user."""
        serializer.save(instructor=self.request.user)


class CourseUpdateView(generics.RetrieveUpdateAPIView):
    """
    Instructor-only endpoint to update their own courses.
    
    GET/PUT/PATCH /api/hub3660/courses/{id}/edit/
    """
    
    serializer_class = CourseCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor]
    
    def get_queryset(self):
        """Return only courses owned by the current instructor."""
        return Course.objects.filter(instructor=self.request.user)


class InstructorCoursesView(generics.ListAPIView):
    """
    Instructor-only endpoint to list their own courses.
    
    GET /api/hub3660/instructor/courses/
    """
    
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor]
    
    def get_queryset(self):
        """Return courses owned by the current instructor."""
        return Course.objects.filter(instructor=self.request.user).select_related('instructor')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def enroll_in_course(request, course_id):
    """
    Student-only endpoint to initiate course enrollment.
    
    POST /api/hub3660/courses/{course_id}/enroll/
    """
    
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.objects.filter(
        student=request.user, 
        course=course
    ).first()
    
    if existing_enrollment:
        if existing_enrollment.payment_status == 'completed':
            return Response(
                {'error': 'You are already enrolled in this course.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif existing_enrollment.payment_status == 'pending':
            return Response(
                {'error': 'You have a pending enrollment for this course.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:  # failed payment, allow retry
            existing_enrollment.delete()
    
    # Create new enrollment
    enrollment_data = {'course': course.id}
    serializer = EnrollmentCreateSerializer(
        data=enrollment_data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        enrollment = serializer.save()
        
        # For free courses, mark as completed immediately
        if course.is_free:
            enrollment.complete_payment('free_course')
            
            # Register for all upcoming Zoom sessions
            _register_student_for_course_sessions(enrollment.student, course)
            
            return Response({
                'message': 'Successfully enrolled in free course.',
                'enrollment_id': enrollment.id,
                'payment_required': False
            }, status=status.HTTP_201_CREATED)
        
        # For paid courses, return enrollment info for payment processing
        return Response({
            'message': 'Enrollment created. Payment required.',
            'enrollment_id': enrollment.id,
            'course_id': course.id,
            'course_title': course.title,
            'amount': str(course.price),
            'currency': course.currency,
            'payment_required': True,
            'payment_metadata': {
                'enrollment_id': enrollment.id,
                'course_id': course.id,
                'course_title': course.title,
                'student_id': request.user.id,
                'student_email': request.user.email
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentEnrollmentsView(generics.ListAPIView):
    """
    Student-only endpoint to list their enrollments.
    
    GET /api/hub3660/student/enrollments/
    """
    
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def get_queryset(self):
        """Return enrollments for the current student."""
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__instructor').order_by('-enrolled_at')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_enrollment_status(request, course_id):
    """
    Check if the current user is enrolled in a specific course.
    
    GET /api/hub3660/courses/{course_id}/enrollment-status/
    """
    
    course = get_object_or_404(Course, id=course_id)
    
    try:
        enrollment = Enrollment.objects.get(student=request.user, course=course)
        return Response({
            'is_enrolled': enrollment.is_active,
            'enrollment_status': enrollment.payment_status,
            'enrolled_at': enrollment.enrolled_at
        })
    except Enrollment.DoesNotExist:
        return Response({
            'is_enrolled': False,
            'enrollment_status': None,
            'enrolled_at': None
        })


class CourseSessionsView(generics.ListAPIView):
    """
    Endpoint to list sessions for a specific course.
    Requires enrollment for detailed session info.
    
    GET /api/hub3660/courses/{course_id}/sessions/
    """
    
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return sessions for the specified course."""
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)
        
        # Check if user is enrolled or is the instructor
        user = self.request.user
        is_enrolled = Enrollment.objects.filter(
            student=user, 
            course=course, 
            payment_status='completed'
        ).exists()
        is_instructor = course.instructor == user
        
        if not (is_enrolled or is_instructor):
            return Session.objects.none()
        
        return Session.objects.filter(course=course).order_by('scheduled_at')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_session_recording(request, session_id):
    """
    Get recording URL for a session with time-limited access.
    Requires enrollment in the course.
    
    GET /api/hub3660/sessions/{session_id}/recording/
    """
    
    session = get_object_or_404(Session, id=session_id)
    user = request.user
    
    # Check if user is enrolled in the course or is the instructor
    is_enrolled = Enrollment.objects.filter(
        student=user,
        course=session.course,
        payment_status='completed'
    ).exists()
    is_instructor = session.course.instructor == user
    
    if not (is_enrolled or is_instructor):
        return Response(
            {'error': 'You must be enrolled in this course to access recordings.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if recording is available
    if not session.has_recording:
        return Response(
            {'error': 'Recording not available for this session.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        # Generate signed URL for S3 recording if available
        if session.s3_recording_key:
            signed_url = recording_storage.generate_signed_url(
                session.s3_recording_key,
                expiration_hours=24
            )
            
            return Response({
                'recording_url': signed_url,
                'session_title': session.title,
                'course_title': session.course.title,
                'expires_in_hours': 24,
                'storage_type': 's3'
            })
        
        # Fallback to original recording URL if S3 not available
        elif session.recording_url:
            return Response({
                'recording_url': session.recording_url,
                'session_title': session.title,
                'course_title': session.course.title,
                'expires_in_hours': None,  # Original URL doesn't expire
                'storage_type': 'zoom'
            })
        
        else:
            return Response(
                {'error': 'Recording not available for this session.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        logger.error(f"Failed to generate recording URL for session {session_id}: {e}")
        
        # Fallback to original URL if S3 fails
        if session.recording_url:
            return Response({
                'recording_url': session.recording_url,
                'session_title': session.title,
                'course_title': session.course.title,
                'expires_in_hours': None,
                'storage_type': 'zoom'
            })
        
        return Response(
            {'error': 'Failed to generate recording access URL. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class SessionCreateView(generics.CreateAPIView):
    """
    Instructor-only endpoint to create new sessions.
    
    POST /api/hub3660/sessions/
    """
    
    serializer_class = SessionCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor]
    
    def perform_create(self, serializer):
        """Create session and Zoom meeting."""
        session = serializer.save()
        
        try:
            # Create Zoom meeting for the session
            zoom_service.create_meeting(session)
            logger.info(f"Created Zoom meeting for session {session.id}")
            
            # Auto-register all enrolled students for the Zoom meeting
            enrolled_students = Enrollment.objects.filter(
                course=session.course,
                payment_status='completed'
            ).select_related('student')
            
            for enrollment in enrolled_students:
                try:
                    zoom_service.register_participant(
                        session,
                        enrollment.student.email,
                        enrollment.student.get_full_name()
                    )
                    logger.info(f"Registered {enrollment.student.email} for session {session.id}")
                except Exception as e:
                    logger.error(f"Failed to register {enrollment.student.email} for session {session.id}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to create Zoom meeting for session {session.id}: {e}")
            # Don't fail the session creation if Zoom fails
            pass


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_student_for_session(request, session_id):
    """
    Register a student for a specific session's Zoom meeting.
    Called when a student enrolls in a course after sessions are already created.
    
    POST /api/hub3660/sessions/{session_id}/register/
    """
    
    session = get_object_or_404(Session, id=session_id)
    user = request.user
    
    # Check if user is enrolled in the course
    is_enrolled = Enrollment.objects.filter(
        student=user,
        course=session.course,
        payment_status='completed'
    ).exists()
    
    if not is_enrolled:
        return Response(
            {'error': 'You must be enrolled in this course to register for sessions.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if not session.zoom_meeting_id:
        return Response(
            {'error': 'This session does not have a Zoom meeting configured.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        zoom_service.register_participant(
            session,
            user.email,
            user.get_full_name()
        )
        
        return Response({
            'message': 'Successfully registered for session.',
            'session_title': session.title,
            'scheduled_at': session.scheduled_at
        })
        
    except Exception as e:
        logger.error(f"Failed to register {user.email} for session {session_id}: {e}")
        return Response(
            {'error': 'Failed to register for session. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def zoom_webhook(request):
    """
    Handle Zoom webhooks for recording completion and other events.
    
    POST /api/hub3660/zoom/webhook/
    """
    
    try:
        # Verify webhook signature if configured
        signature = request.META.get('HTTP_AUTHORIZATION', '')
        if signature.startswith('Bearer '):
            signature = signature[7:]
        
        if not zoom_service.verify_webhook_signature(request.body, signature):
            logger.warning("Invalid Zoom webhook signature")
            return HttpResponse(status=401)
        
        # Parse webhook payload
        webhook_data = json.loads(request.body)
        
        # Process the webhook
        success = zoom_service.process_recording_webhook(webhook_data)
        
        if success:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Zoom webhook payload")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Error processing Zoom webhook: {e}")
        return HttpResponse(status=500)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_course_recordings(request, course_id):
    """
    Get all available recordings for a course.
    Requires enrollment in the course.
    
    GET /api/hub3660/courses/{course_id}/recordings/
    """
    
    course = get_object_or_404(Course, id=course_id)
    user = request.user
    
    # Check if user is enrolled in the course or is the instructor
    is_enrolled = Enrollment.objects.filter(
        student=user,
        course=course,
        payment_status='completed'
    ).exists()
    is_instructor = course.instructor == user
    
    if not (is_enrolled or is_instructor):
        return Response(
            {'error': 'You must be enrolled in this course to access recordings.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get all sessions with recordings for this course
    sessions_with_recordings = Session.objects.filter(
        course=course
    ).filter(
        Q(s3_recording_key__isnull=False) | Q(recording_url__isnull=False)
    ).order_by('-scheduled_at')
    
    recordings = []
    for session in sessions_with_recordings:
        try:
            recording_data = {
                'session_id': session.id,
                'session_title': session.title,
                'scheduled_at': session.scheduled_at,
                'has_recording': session.has_recording
            }
            
            # Generate signed URL if S3 recording is available
            if session.s3_recording_key:
                try:
                    signed_url = recording_storage.generate_signed_url(
                        session.s3_recording_key,
                        expiration_hours=24
                    )
                    recording_data.update({
                        'recording_url': signed_url,
                        'expires_in_hours': 24,
                        'storage_type': 's3'
                    })
                except Exception as e:
                    logger.error(f"Failed to generate signed URL for session {session.id}: {e}")
                    # Skip this recording if S3 fails
                    continue
            
            # Fallback to original URL
            elif session.recording_url:
                recording_data.update({
                    'recording_url': session.recording_url,
                    'expires_in_hours': None,
                    'storage_type': 'zoom'
                })
            
            recordings.append(recording_data)
            
        except Exception as e:
            logger.error(f"Error processing recording for session {session.id}: {e}")
            continue
    
    return Response({
        'course_id': course.id,
        'course_title': course.title,
        'recordings': recordings,
        'total_recordings': len(recordings)
    })


def _register_student_for_course_sessions(student, course):
    """
    Helper function to register a student for all upcoming sessions in a course.
    
    Args:
        student: User instance of the student
        course: Course instance
    """
    from django.utils import timezone
    
    # Get all upcoming sessions with Zoom meetings
    upcoming_sessions = Session.objects.filter(
        course=course,
        scheduled_at__gte=timezone.now(),
        zoom_meeting_id__isnull=False
    )
    
    for session in upcoming_sessions:
        try:
            zoom_service.register_participant(
                session,
                student.email,
                student.get_full_name()
            )
            logger.info(f"Auto-registered {student.email} for session {session.id}")
        except Exception as e:
            logger.error(f"Failed to auto-register {student.email} for session {session.id}: {e}")
            # Continue with other sessions even if one fails