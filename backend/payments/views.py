"""
Payment views for handling payment sessions and webhooks.
"""
import logging
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods

from .models import Transaction
from .serializers import (
    TransactionSerializer,
    PaymentSessionCreateSerializer,
    PaymentProviderRoutingSerializer,
    WebhookEventSerializer
)
from .services import PaymentSessionService, TransactionService, PaymentProviderRouter

User = get_user_model()
logger = logging.getLogger(__name__)


class PaymentSessionCreateView(APIView):
    """
    Create a payment session with the appropriate provider.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create a new payment session."""
        serializer = PaymentSessionCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get country code from request headers or user profile
            country_code = request.META.get('HTTP_CF_IPCOUNTRY')  # Cloudflare header
            if not country_code:
                country_code = request.data.get('country_code')
            
            session_data = PaymentSessionService.create_payment_session(
                user=request.user,
                amount=serializer.validated_data['amount'],
                currency=serializer.validated_data['currency'],
                success_url=serializer.validated_data['success_url'],
                cancel_url=serializer.validated_data['cancel_url'],
                metadata=serializer.validated_data.get('metadata', {}),
                country_code=country_code
            )
            
            return Response(session_data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating payment session: {str(e)}")
            return Response(
                {'error': 'Failed to create payment session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentProviderRoutingView(APIView):
    """
    Get the appropriate payment provider for a user's location and currency.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Get payment provider routing information."""
        serializer = PaymentProviderRoutingSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        country_code = serializer.validated_data.get('country_code')
        currency = serializer.validated_data.get('currency', 'USD')
        
        # Get country code from headers if not provided
        if not country_code:
            country_code = request.META.get('HTTP_CF_IPCOUNTRY')
        
        provider = PaymentProviderRouter.get_provider(country_code, currency)
        is_configured = PaymentProviderRouter.is_provider_configured(provider)
        
        return Response({
            'provider': provider,
            'country_code': country_code,
            'currency': currency,
            'is_configured': is_configured,
            'config': PaymentProviderRouter.get_provider_config(provider) if is_configured else {}
        })


class TransactionListView(APIView):
    """
    List user's transactions.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's transaction history."""
        status_filter = request.query_params.get('status')
        transactions = TransactionService.get_user_transactions(
            user=request.user,
            status=status_filter
        )
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class TransactionDetailView(APIView):
    """
    Get details of a specific transaction.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, transaction_id):
        """Get transaction details."""
        try:
            transaction = Transaction.objects.get(
                id=transaction_id,
                user=request.user
            )
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data)
            
        except Transaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    Handle Stripe webhook events.
    """
    permission_classes = []  # Webhooks don't use authentication
    
    def post(self, request):
        """Handle Stripe webhook."""
        try:
            from .stripe_service import StripeService
            
            # Get the raw body and signature
            payload = request.body
            signature = request.META.get('HTTP_STRIPE_SIGNATURE', '')
            
            # Process the webhook event
            success = StripeService.handle_webhook_event(payload, signature)
            
            if success:
                return Response({'status': 'success'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {str(e)}")
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(APIView):
    """
    Handle Paystack webhook events.
    """
    permission_classes = []  # Webhooks don't use authentication
    
    def post(self, request):
        """Handle Paystack webhook."""
        try:
            from .paystack_service import PaystackService
            
            # Get the raw body and signature
            payload = request.body
            signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
            
            # Process the webhook event
            success = PaystackService.handle_webhook_event(payload, signature)
            
            if success:
                return Response({'status': 'success'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error processing Paystack webhook: {str(e)}")
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_status(request, transaction_id):
    """
    Get the current status of a payment transaction.
    """
    try:
        transaction = Transaction.objects.get(
            id=transaction_id,
            user=request.user
        )
        
        return Response({
            'transaction_id': transaction.id,
            'status': transaction.status,
            'amount': transaction.amount,
            'currency': transaction.currency,
            'provider': transaction.provider,
            'created_at': transaction.created_at,
            'updated_at': transaction.updated_at,
        })
        
    except Transaction.DoesNotExist:
        return Response(
            {'error': 'Transaction not found'},
            status=status.HTTP_404_NOT_FOUND
        )