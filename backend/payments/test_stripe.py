"""
Tests for Stripe integration.
"""
import json
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Transaction
from .stripe_service import StripeService

User = get_user_model()


class StripeServiceTest(TestCase):
    """Test Stripe service functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    @patch('payments.stripe_service.stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_stripe_create):
        """Test creating Stripe checkout session."""
        # Mock Stripe response
        mock_session = MagicMock()
        mock_session.id = 'cs_test_123456'
        mock_session.url = 'https://checkout.stripe.com/pay/cs_test_123456'
        mock_session.payment_intent = 'pi_test_123456'
        mock_session.expires_at = 1234567890
        mock_stripe_create.return_value = mock_session
        
        result = StripeService.create_checkout_session(
            user=self.user,
            amount=99.99,
            currency='USD',
            success_url='http://localhost:3000/success',
            cancel_url='http://localhost:3000/cancel',
            metadata={'course_id': 1}
        )
        
        # Verify Stripe was called correctly
        mock_stripe_create.assert_called_once()
        call_args = mock_stripe_create.call_args[1]
        self.assertEqual(call_args['line_items'][0]['price_data']['unit_amount'], 9999)  # 99.99 * 100
        self.assertEqual(call_args['customer_email'], 'test@example.com')
        self.assertEqual(call_args['metadata']['user_id'], str(self.user.id))
        
        # Verify return data
        self.assertEqual(result['session_id'], 'cs_test_123456')
        self.assertEqual(result['session_url'], 'https://checkout.stripe.com/pay/cs_test_123456')
        self.assertEqual(result['provider'], 'stripe')
        self.assertEqual(result['amount'], 99.99)
        self.assertEqual(result['currency'], 'USD')
        
        # Verify transaction was created
        transaction = Transaction.objects.get(provider_transaction_id='cs_test_123456')
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal('99.99'))
        self.assertEqual(transaction.provider, 'stripe')
        self.assertEqual(transaction.status, 'pending')
    
    @patch('payments.stripe_service.stripe.Webhook.construct_event')
    def test_handle_webhook_checkout_completed(self, mock_construct_event):
        """Test handling Stripe checkout completion webhook."""
        # Create a transaction first
        transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            currency='USD',
            provider='stripe',
            provider_transaction_id='cs_test_webhook',
            status='pending'
        )
        
        # Mock webhook event
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_webhook',
                    'payment_status': 'paid',
                    'payment_intent': 'pi_test_webhook',
                    'customer': 'cus_test_123',
                    'created': 1234567890
                }
            }
        }
        mock_construct_event.return_value = mock_event
        
        # Process webhook
        success = StripeService.handle_webhook_event(
            event_data=json.dumps(mock_event).encode(),
            signature='test_signature'
        )
        
        self.assertTrue(success)
        
        # Verify transaction was updated
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, 'completed')
        self.assertEqual(transaction.metadata['stripe_payment_intent'], 'pi_test_webhook')
    
    @patch('payments.stripe_service.stripe.Webhook.construct_event')
    def test_handle_webhook_payment_failed(self, mock_construct_event):
        """Test handling Stripe payment failure webhook."""
        # Create a transaction first
        transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('75.00'),
            currency='USD',
            provider='stripe',
            provider_transaction_id='cs_test_failed',
            status='pending',
            metadata={'stripe_payment_intent': 'pi_test_failed'}
        )
        
        # Mock webhook event
        mock_event = {
            'type': 'payment_intent.payment_failed',
            'data': {
                'object': {
                    'id': 'pi_test_failed',
                    'status': 'requires_payment_method',
                    'last_payment_error': {
                        'message': 'Your card was declined.'
                    },
                    'created': 1234567890
                }
            }
        }
        mock_construct_event.return_value = mock_event
        
        # Process webhook
        success = StripeService.handle_webhook_event(
            event_data=json.dumps(mock_event).encode(),
            signature='test_signature'
        )
        
        self.assertTrue(success)
        
        # Verify transaction was updated
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, 'failed')
        self.assertEqual(transaction.metadata['stripe_failure_reason'], 'Your card was declined.')
    
    @patch('payments.stripe_service.stripe.checkout.Session.retrieve')
    def test_retrieve_session(self, mock_retrieve):
        """Test retrieving Stripe session."""
        # Mock Stripe response
        mock_session = MagicMock()
        mock_session.id = 'cs_test_retrieve'
        mock_session.payment_status = 'paid'
        mock_session.payment_intent = 'pi_test_retrieve'
        mock_session.customer = 'cus_test_retrieve'
        mock_session.amount_total = 5000
        mock_session.currency = 'usd'
        mock_session.metadata = {'user_id': '1'}
        mock_session.created = 1234567890
        mock_session.expires_at = 1234569690
        mock_retrieve.return_value = mock_session
        
        result = StripeService.retrieve_session('cs_test_retrieve')
        
        self.assertEqual(result['id'], 'cs_test_retrieve')
        self.assertEqual(result['payment_status'], 'paid')
        self.assertEqual(result['amount_total'], 5000)
        self.assertEqual(result['currency'], 'usd')
    
    @patch('payments.stripe_service.stripe.Refund.create')
    def test_create_refund(self, mock_refund_create):
        """Test creating Stripe refund."""
        # Mock Stripe response
        mock_refund = MagicMock()
        mock_refund.id = 're_test_123'
        mock_refund.amount = 5000
        mock_refund.currency = 'usd'
        mock_refund.status = 'succeeded'
        mock_refund.reason = 'requested_by_customer'
        mock_refund.created = 1234567890
        mock_refund_create.return_value = mock_refund
        
        result = StripeService.create_refund(
            payment_intent_id='pi_test_refund',
            amount=5000,
            reason='requested_by_customer'
        )
        
        # Verify Stripe was called correctly
        mock_refund_create.assert_called_once_with(
            payment_intent='pi_test_refund',
            amount=5000,
            reason='requested_by_customer'
        )
        
        # Verify return data
        self.assertEqual(result['refund_id'], 're_test_123')
        self.assertEqual(result['amount'], 5000)
        self.assertEqual(result['status'], 'succeeded')


class StripeWebhookAPITest(APITestCase):
    """Test Stripe webhook API endpoint."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    @patch('payments.stripe_service.StripeService.handle_webhook_event')
    def test_stripe_webhook_endpoint(self, mock_handle_webhook):
        """Test Stripe webhook endpoint."""
        mock_handle_webhook.return_value = True
        
        url = '/api/payments/webhook/stripe/'
        webhook_data = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_webhook_api',
                    'payment_status': 'paid'
                }
            }
        }
        
        response = self.client.post(
            url,
            data=json.dumps(webhook_data),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        # Verify the service was called
        mock_handle_webhook.assert_called_once()
    
    @patch('payments.stripe_service.StripeService.handle_webhook_event')
    def test_stripe_webhook_endpoint_failure(self, mock_handle_webhook):
        """Test Stripe webhook endpoint with failure."""
        mock_handle_webhook.return_value = False
        
        url = '/api/payments/webhook/stripe/'
        webhook_data = {
            'type': 'invalid.event',
            'data': {}
        }
        
        response = self.client.post(
            url,
            data=json.dumps(webhook_data),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='invalid_signature'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')


class StripeIntegrationTest(APITestCase):
    """Test complete Stripe integration flow."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    @patch('payments.services.PaymentProviderRouter.is_provider_configured')
    @patch('payments.stripe_service.stripe.checkout.Session.create')
    def test_complete_stripe_payment_flow(self, mock_stripe_create, mock_is_configured):
        """Test complete payment flow with Stripe."""
        # Mock configuration check
        mock_is_configured.return_value = True
        
        # Mock Stripe session creation
        mock_session = MagicMock()
        mock_session.id = 'cs_test_integration'
        mock_session.url = 'https://checkout.stripe.com/pay/cs_test_integration'
        mock_session.payment_intent = 'pi_test_integration'
        mock_session.expires_at = 1234567890
        mock_stripe_create.return_value = mock_session
        
        # Create payment session
        url = '/api/payments/create-checkout/'
        data = {
            'amount': '149.99',
            'currency': 'USD',
            'success_url': 'http://localhost:3000/success',
            'cancel_url': 'http://localhost:3000/cancel',
            'metadata': {'course_id': 2}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['provider'], 'stripe')
        self.assertEqual(response.data['session_id'], 'cs_test_integration')
        self.assertIn('session_url', response.data)
        
        # Verify transaction was created
        transaction = Transaction.objects.get(provider_transaction_id='cs_test_integration')
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal('149.99'))
        self.assertEqual(transaction.status, 'pending')