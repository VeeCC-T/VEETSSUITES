"""
Tests for Paystack integration.
"""
import json
import hashlib
import hmac
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Transaction
from .paystack_service import PaystackService

User = get_user_model()


class PaystackServiceTest(TestCase):
    """Test Paystack service functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    @patch('payments.paystack_service.PaystackTransaction.initialize')
    def test_create_checkout_session(self, mock_paystack_init):
        """Test creating Paystack checkout session."""
        # Mock Paystack response
        mock_response = {
            'status': True,
            'data': {
                'reference': 'ps_test_123456',
                'authorization_url': 'https://checkout.paystack.com/ps_test_123456',
                'access_code': 'access_code_123'
            }
        }
        mock_paystack_init.return_value = mock_response
        
        result = PaystackService.create_checkout_session(
            user=self.user,
            amount=99.99,
            currency='NGN',
            success_url='http://localhost:3000/success',
            cancel_url='http://localhost:3000/cancel',
            metadata={'course_id': 1}
        )
        
        # Verify Paystack was called correctly
        mock_paystack_init.assert_called_once()
        call_args = mock_paystack_init.call_args[1]
        self.assertEqual(call_args['email'], 'test@example.com')
        self.assertEqual(call_args['amount'], 9999)  # 99.99 * 100
        self.assertEqual(call_args['currency'], 'NGN')
        self.assertEqual(call_args['callback_url'], 'http://localhost:3000/success')
        
        # Verify return data
        self.assertEqual(result['session_id'], 'ps_test_123456')
        self.assertEqual(result['session_url'], 'https://checkout.paystack.com/ps_test_123456')
        self.assertEqual(result['provider'], 'paystack')
        self.assertEqual(result['amount'], 99.99)
        self.assertEqual(result['currency'], 'NGN')
        
        # Verify transaction was created
        transaction = Transaction.objects.get(provider_transaction_id='ps_test_123456')
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal('99.99'))
        self.assertEqual(transaction.provider, 'paystack')
        self.assertEqual(transaction.status, 'pending')
    
    @patch('payments.paystack_service.PaystackTransaction.initialize')
    def test_create_checkout_session_failure(self, mock_paystack_init):
        """Test Paystack checkout session creation failure."""
        # Mock Paystack failure response
        mock_response = {
            'status': False,
            'message': 'Invalid email address'
        }
        mock_paystack_init.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            PaystackService.create_checkout_session(
                user=self.user,
                amount=50.00,
                currency='NGN',
                success_url='http://localhost:3000/success',
                cancel_url='http://localhost:3000/cancel'
            )
        
        self.assertIn('Invalid email address', str(context.exception))
    
    def test_verify_webhook_signature(self):
        """Test Paystack webhook signature verification."""
        # Create test payload and signature
        payload = b'{"event": "charge.success", "data": {"reference": "test_ref"}}'
        
        # Create expected signature
        expected_signature = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        signature_header = f'sha512={expected_signature}'
        
        # Test valid signature
        is_valid = PaystackService._verify_webhook_signature(payload, signature_header)
        self.assertTrue(is_valid)
        
        # Test invalid signature
        invalid_signature = 'sha512=invalid_signature'
        is_valid = PaystackService._verify_webhook_signature(payload, invalid_signature)
        self.assertFalse(is_valid)
        
        # Test malformed signature
        malformed_signature = 'invalid_format'
        is_valid = PaystackService._verify_webhook_signature(payload, malformed_signature)
        self.assertFalse(is_valid)
    
    def test_handle_webhook_charge_success(self):
        """Test handling Paystack charge success webhook."""
        # Create a transaction first
        transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            currency='NGN',
            provider='paystack',
            provider_transaction_id='ps_test_webhook',
            status='pending'
        )
        
        # Create webhook payload
        webhook_data = {
            'event': 'charge.success',
            'data': {
                'reference': 'ps_test_webhook',
                'status': 'success',
                'gateway_response': 'Successful',
                'paid_at': '2023-01-01T12:00:00.000Z',
                'channel': 'card',
                'fees': 150
            }
        }
        
        payload = json.dumps(webhook_data).encode('utf-8')
        signature = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        signature_header = f'sha512={signature}'
        
        # Process webhook
        success = PaystackService.handle_webhook_event(payload, signature_header)
        
        self.assertTrue(success)
        
        # Verify transaction was updated
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, 'completed')
        self.assertEqual(transaction.metadata['paystack_gateway_response'], 'Successful')
        self.assertEqual(transaction.metadata['paystack_channel'], 'card')
    
    def test_handle_webhook_charge_failed(self):
        """Test handling Paystack charge failure webhook."""
        # Create a transaction first
        transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('75.00'),
            currency='NGN',
            provider='paystack',
            provider_transaction_id='ps_test_failed',
            status='pending'
        )
        
        # Create webhook payload
        webhook_data = {
            'event': 'charge.failed',
            'data': {
                'reference': 'ps_test_failed',
                'status': 'failed',
                'gateway_response': 'Declined by bank',
                'channel': 'card'
            }
        }
        
        payload = json.dumps(webhook_data).encode('utf-8')
        signature = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        signature_header = f'sha512={signature}'
        
        # Process webhook
        success = PaystackService.handle_webhook_event(payload, signature_header)
        
        self.assertTrue(success)
        
        # Verify transaction was updated
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, 'failed')
        self.assertEqual(transaction.metadata['paystack_failure_reason'], 'Declined by bank')
    
    @patch('payments.paystack_service.PaystackTransaction.verify')
    def test_verify_transaction(self, mock_verify):
        """Test verifying Paystack transaction."""
        # Mock Paystack response
        mock_response = {
            'status': True,
            'data': {
                'reference': 'ps_test_verify',
                'status': 'success',
                'amount': 5000,
                'currency': 'NGN',
                'channel': 'card',
                'fees': 150,
                'gateway_response': 'Successful',
                'paid_at': '2023-01-01T12:00:00.000Z',
                'created_at': '2023-01-01T11:00:00.000Z',
                'metadata': {'user_id': '1'}
            }
        }
        mock_verify.return_value = mock_response
        
        result = PaystackService.verify_transaction('ps_test_verify')
        
        self.assertEqual(result['reference'], 'ps_test_verify')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['amount'], 5000)
        self.assertEqual(result['currency'], 'NGN')
        self.assertEqual(result['channel'], 'card')
    
    @patch('payments.paystack_service.PaystackService.verify_transaction')
    def test_create_refund(self, mock_verify):
        """Test creating Paystack refund."""
        # Mock transaction verification
        mock_verify.return_value = {
            'reference': 'ps_test_refund',
            'status': 'success',
            'amount': 5000,
            'currency': 'NGN',
            'created_at': '2023-01-01T12:00:00.000Z'
        }
        
        result = PaystackService.create_refund(
            transaction_reference='ps_test_refund',
            amount=5000,
            reason='requested_by_customer'
        )
        
        # Verify return data (mock implementation)
        self.assertEqual(result['refund_id'], 'rf_ps_test_refund')
        self.assertEqual(result['amount'], 5000)
        self.assertEqual(result['currency'], 'NGN')
        self.assertEqual(result['status'], 'pending')
    
    def test_get_payment_channels(self):
        """Test getting Paystack payment channels."""
        channels = PaystackService.get_payment_channels()
        expected_channels = ['card', 'bank', 'ussd', 'qr', 'mobile_money', 'bank_transfer']
        self.assertEqual(channels, expected_channels)
    
    def test_get_supported_currencies(self):
        """Test getting Paystack supported currencies."""
        currencies = PaystackService.get_supported_currencies()
        expected_currencies = ['NGN', 'USD', 'GHS', 'ZAR', 'KES']
        self.assertEqual(currencies, expected_currencies)


class PaystackWebhookAPITest(APITestCase):
    """Test Paystack webhook API endpoint."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    @patch('payments.paystack_service.PaystackService.handle_webhook_event')
    def test_paystack_webhook_endpoint(self, mock_handle_webhook):
        """Test Paystack webhook endpoint."""
        mock_handle_webhook.return_value = True
        
        url = '/api/payments/webhook/paystack/'
        webhook_data = {
            'event': 'charge.success',
            'data': {
                'reference': 'ps_test_webhook_api',
                'status': 'success'
            }
        }
        
        response = self.client.post(
            url,
            data=json.dumps(webhook_data),
            content_type='application/json',
            HTTP_X_PAYSTACK_SIGNATURE='sha512=test_signature'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        # Verify the service was called
        mock_handle_webhook.assert_called_once()
    
    @patch('payments.paystack_service.PaystackService.handle_webhook_event')
    def test_paystack_webhook_endpoint_failure(self, mock_handle_webhook):
        """Test Paystack webhook endpoint with failure."""
        mock_handle_webhook.return_value = False
        
        url = '/api/payments/webhook/paystack/'
        webhook_data = {
            'event': 'invalid.event',
            'data': {}
        }
        
        response = self.client.post(
            url,
            data=json.dumps(webhook_data),
            content_type='application/json',
            HTTP_X_PAYSTACK_SIGNATURE='sha512=invalid_signature'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')


class PaystackIntegrationTest(APITestCase):
    """Test complete Paystack integration flow."""
    
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
    @patch('payments.paystack_service.PaystackTransaction.initialize')
    def test_complete_paystack_payment_flow(self, mock_paystack_init, mock_is_configured):
        """Test complete payment flow with Paystack."""
        # Mock configuration check
        mock_is_configured.return_value = True
        
        # Mock Paystack initialization
        mock_response = {
            'status': True,
            'data': {
                'reference': 'ps_test_integration',
                'authorization_url': 'https://checkout.paystack.com/ps_test_integration',
                'access_code': 'access_code_integration'
            }
        }
        mock_paystack_init.return_value = mock_response
        
        # Create payment session with Nigerian currency to trigger Paystack
        url = '/api/payments/create-checkout/'
        data = {
            'amount': '149.99',
            'currency': 'NGN',
            'success_url': 'http://localhost:3000/success',
            'cancel_url': 'http://localhost:3000/cancel',
            'metadata': {'course_id': 2}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['provider'], 'paystack')
        self.assertEqual(response.data['session_id'], 'ps_test_integration')
        self.assertIn('session_url', response.data)
        
        # Verify transaction was created
        transaction = Transaction.objects.get(provider_transaction_id='ps_test_integration')
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal('149.99'))
        self.assertEqual(transaction.status, 'pending')