from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.permissions import IsPharmacist
from .models import Consultation, ConsultationMessage
from .serializers import (
    ConsultationSerializer, ConsultationCreateSerializer,
    MessageCreateSerializer, ConsultationMessageSerializer,
    PharmacistQueueSerializer
)

User = get_user_model()


class ConsultationListCreateView(generics.ListCreateAPIView):
    """
    List user's consultations or create a new consultation
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Consultation.objects.filter(user=self.request.user).prefetch_related('messages')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ConsultationCreateSerializer
        return ConsultationSerializer
    
    def perform_create(self, serializer):
        consultation = serializer.save(user=self.request.user)
        
        # If it's a human consultation, set status to waiting
        if consultation.consultation_type == 'human':
            consultation.status = 'waiting'
            consultation.save()


class ConsultationDetailView(generics.RetrieveAPIView):
    """
    Get consultation details with messages
    """
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Consultation.objects.filter(user=self.request.user).prefetch_related('messages__sender')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, consultation_id):
    """
    Send a message in a consultation and get AI response if applicable
    """
    from .ai_service import ai_service
    
    consultation = get_object_or_404(
        Consultation, 
        id=consultation_id, 
        user=request.user
    )
    
    # Check if consultation is still active
    if consultation.status == 'completed':
        return Response(
            {'error': 'Cannot send messages to completed consultation'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = MessageCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Save user message
        user_message = serializer.save(
            consultation=consultation,
            sender=request.user
        )
        
        response_data = {
            'user_message': ConsultationMessageSerializer(user_message).data,
            'ai_response': None
        }
        
        # If this is an AI consultation, get AI response
        if consultation.consultation_type == 'ai':
            try:
                # Get conversation history for context
                previous_messages = consultation.messages.all().order_by('created_at')
                
                # Get AI response
                ai_result = ai_service.get_ai_response(
                    message=user_message.message,
                    conversation_messages=list(previous_messages)
                )
                
                # Create AI response message
                ai_message = ConsultationMessage.objects.create(
                    consultation=consultation,
                    sender=request.user,  # AI responses are associated with the user for simplicity
                    message=ai_result['response'],
                    is_ai_response=True
                )
                
                response_data['ai_response'] = ConsultationMessageSerializer(ai_message).data
                response_data['ai_metadata'] = {
                    'success': ai_result['success'],
                    'cached': ai_result['cached'],
                    'error': ai_result['error']
                }
                
            except Exception as e:
                # Log error but don't fail the request
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"AI response error: {e}")
                
                # Create fallback message
                fallback_message = ConsultationMessage.objects.create(
                    consultation=consultation,
                    sender=request.user,
                    message="I'm currently experiencing technical difficulties. Please try again or request a human pharmacist for assistance.",
                    is_ai_response=True
                )
                
                response_data['ai_response'] = ConsultationMessageSerializer(fallback_message).data
                response_data['ai_metadata'] = {
                    'success': False,
                    'cached': False,
                    'error': 'AI service temporarily unavailable'
                }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consultation_messages(request, consultation_id):
    """
    Get all messages for a consultation
    """
    consultation = get_object_or_404(
        Consultation, 
        id=consultation_id, 
        user=request.user
    )
    
    messages = consultation.messages.all().select_related('sender')
    serializer = ConsultationMessageSerializer(messages, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_pharmacist(request, consultation_id):
    """
    Request human pharmacist for a consultation
    """
    consultation = get_object_or_404(
        Consultation, 
        id=consultation_id, 
        user=request.user
    )
    
    # Only allow if consultation is currently AI type
    if consultation.consultation_type != 'ai':
        return Response(
            {'error': 'Can only request pharmacist for AI consultations'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update consultation to human type and set status to waiting
    consultation.consultation_type = 'human'
    consultation.status = 'waiting'
    consultation.save()
    
    # Add a system message
    ConsultationMessage.objects.create(
        consultation=consultation,
        sender=request.user,
        message="Requested human pharmacist assistance",
        is_ai_response=False
    )
    
    serializer = ConsultationSerializer(consultation)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsPharmacist])
def pharmacist_queue(request):
    """
    Get queue of consultations waiting for pharmacist (pharmacist only)
    """
    waiting_consultations = Consultation.objects.filter(
        consultation_type='human',
        status='waiting',
        pharmacist__isnull=True
    ).select_related('user').prefetch_related('messages')
    
    serializer = PharmacistQueueSerializer(waiting_consultations, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsPharmacist])
def accept_consultation(request, consultation_id):
    """
    Accept a consultation from the queue (pharmacist only)
    """
    consultation = get_object_or_404(
        Consultation, 
        id=consultation_id,
        consultation_type='human',
        status='waiting',
        pharmacist__isnull=True
    )
    
    # Assign pharmacist and set status to active
    consultation.pharmacist = request.user
    consultation.status = 'active'
    consultation.save()
    
    # Add a system message
    ConsultationMessage.objects.create(
        consultation=consultation,
        sender=request.user,
        message=f"Pharmacist {request.user.get_full_name() or request.user.email} has joined the consultation",
        is_ai_response=False
    )
    
    serializer = ConsultationSerializer(consultation)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_consultation(request, consultation_id):
    """
    Complete a consultation
    """
    consultation = get_object_or_404(
        Consultation, 
        id=consultation_id
    )
    
    # Check permissions - user or assigned pharmacist can complete
    if consultation.user != request.user and consultation.pharmacist != request.user:
        return Response(
            {'error': 'You do not have permission to complete this consultation'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    consultation.status = 'completed'
    consultation.completed_at = timezone.now()
    consultation.save()
    
    # Add completion message
    ConsultationMessage.objects.create(
        consultation=consultation,
        sender=request.user,
        message="Consultation completed",
        is_ai_response=False
    )
    
    serializer = ConsultationSerializer(consultation)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_health_check(request):
    """
    Check AI service health status
    """
    from .ai_service import ai_service
    
    try:
        health_status = ai_service.health_check()
        return Response({
            'ai_service': health_status,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return Response({
            'ai_service': {
                'available': False,
                'response_time': None,
                'error': str(e)
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)