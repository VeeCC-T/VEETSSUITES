"""
HUB3660 serializers for API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Enrollment, Session

User = get_user_model()


class InstructorSerializer(serializers.ModelSerializer):
    """Serializer for instructor information in course details."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email']
        read_only_fields = ['id', 'first_name', 'last_name', 'full_name', 'email']


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for course list view."""
    
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    enrollment_count = serializers.ReadOnlyField()
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'instructor_name', 
            'price', 'currency', 'enrollment_count', 'is_enrolled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'instructor_name', 'enrollment_count', 'created_at', 'updated_at']
    
    def get_is_enrolled(self, obj):
        """Check if the current user is enrolled in this course."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                student=request.user,
                course=obj,
                payment_status='completed'
            ).exists()
        return False


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed course view."""
    
    instructor = InstructorSerializer(read_only=True)
    enrollment_count = serializers.ReadOnlyField()
    is_enrolled = serializers.SerializerMethodField()
    enrollment_status = serializers.SerializerMethodField()
    sessions = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'instructor', 'price', 'currency',
            'enrollment_count', 'is_enrolled', 'enrollment_status', 'sessions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'instructor', 'enrollment_count', 'created_at', 'updated_at']
    
    def get_is_enrolled(self, obj):
        """Check if the current user is enrolled in this course."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                student=request.user,
                course=obj,
                payment_status='completed'
            ).exists()
        return False
    
    def get_enrollment_status(self, obj):
        """Get the enrollment status for the current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(student=request.user, course=obj)
                return enrollment.payment_status
            except Enrollment.DoesNotExist:
                return None
        return None
    
    def get_sessions(self, obj):
        """Get upcoming sessions for this course."""
        from django.utils import timezone
        upcoming_sessions = obj.sessions.filter(scheduled_at__gte=timezone.now()).order_by('scheduled_at')
        return SessionSerializer(upcoming_sessions, many=True).data


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating courses."""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'currency', 'is_published']
    
    def validate_price(self, value):
        """Validate that price is not negative."""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value
    
    def create(self, validated_data):
        """Create a new course with the current user as instructor."""
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for enrollment information."""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_title', 'student_name', 
            'payment_status', 'payment_id', 'enrolled_at'
        ]
        read_only_fields = ['id', 'course_title', 'student_name', 'enrolled_at']


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating enrollments."""
    
    class Meta:
        model = Enrollment
        fields = ['course']
    
    def validate_course(self, value):
        """Validate enrollment requirements."""
        user = self.context['request'].user
        
        # Check if user is already enrolled
        if Enrollment.objects.filter(student=user, course=value).exists():
            raise serializers.ValidationError("You are already enrolled in this course.")
        
        # Check if course is published
        if not value.is_published:
            raise serializers.ValidationError("This course is not available for enrollment.")
        
        return value
    
    def create(self, validated_data):
        """Create enrollment with current user as student."""
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for session information."""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    is_upcoming = serializers.ReadOnlyField()
    has_recording = serializers.ReadOnlyField()
    
    class Meta:
        model = Session
        fields = [
            'id', 'title', 'course_title', 'scheduled_at', 
            'zoom_join_url', 'recording_url', 'is_upcoming', 
            'has_recording', 'created_at'
        ]
        read_only_fields = [
            'id', 'course_title', 'is_upcoming', 'has_recording', 'created_at'
        ]


class SessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sessions."""
    
    class Meta:
        model = Session
        fields = ['course', 'title', 'scheduled_at']
    
    def validate_course(self, value):
        """Validate that the instructor owns the course."""
        user = self.context['request'].user
        if value.instructor != user:
            raise serializers.ValidationError("You can only create sessions for your own courses.")
        return value
    
    def validate_scheduled_at(self, value):
        """Validate that the session is scheduled in the future."""
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Session must be scheduled in the future.")
        return value