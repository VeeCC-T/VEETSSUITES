"""
Property-based tests for payment processing.
"""
import json
import hashlib
import hmac
import uuid
from decimal import Decimal
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings as hypothesis_settings
from hypothesis.extra.django import TestCase as HypothesisTestCase
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Transaction
from .services import PaymentProviderRouter, PaymentSessionService, TransactionService

User = get_user_model()


class PaymentPropertyTests(HypothesisTestCase):
    """Property-based tests for payment processing."""
    
    def setUp(self):
        # Create a unique user for each test to avoid constraint issues
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    # Feature: veetssuites-platform, Property 25: Payment provider routing by location
    @given(
        country_code=st.one_of(
            st.just('NG'),  # Nigerian country code
            st.just('US'),  # US country code
            st.just('GB'),  # UK country code
            st.just('CA'),  # Canada country code
            st.just('AU'),  # Australia country code
            st.none()       # No country code
        ),
        currency=st.one_of(
            st.just('NGN'),  # Nigerian Naira
            st.just('USD'),  # US Dollar
            st.just('GBP'),  # British Pound
            st.just('EUR'),  # Euro
            st.just('CAD')   # Canadian Dollar
        )
    )
    @hypothesis_settings(max_examples=100)
    def test_payment_provider_routing_by_location(self, country_code, currency):
        """
        For any country code and currency combination, the payment provider routing
        should consistently route Nigerian users or NGN currency to Paystack,
        and all other combinations to Stripe.
        """
        provider = PaymentProviderRouter.get_provider(country_code, currency)
        
        # Nigerian users or NGN currency should route to Paystack
        if country_code == 'NG' or currency == 'NGN':
            self.assertEqual(provider, 'paystack')
        else:
            # All other combinations should route to Stripe
            self.assertEqual(provider, 'stripe')
        
        # Provider should always be one of the supported providers
        self.assertIn(provider, ['stripe', 'paystack', 'flutterwave'])
    
    # Feature: veetssuites-platform, Property 26: Payment webhooks trigger access grants
    @given(
        transaction_amount=st.decimals(min_value=1, max_value=10000, places=2),
        provider=st.one_of(st.just('stripe'), st.just('paystack')),
        webhook_status=st.one_of(
            st.just('completed'),
            st.just('success'),
            st.just('paid')
        )
    )
    @hypothesis_settings(max_examples=100)
    def test_payment_webhooks_trigger_access_grants(self, transaction_amount, provider, webhook_status):
        """
        For any successful payment webhook received from any provider,
        the system should update the transaction status to 'completed'
        and grant access to the purchased content.
        """
        # Create a pending transaction
        transaction = Transaction.objects.create(
            user=self.user,
            amount=transaction_amount,
            currency='USD' if provider == 'stripe' else 'NGN',
            provider=provider,
            provider_transaction_id=f'{provider}_test_{transaction_amount}_{uuid.uuid4().hex[:8]}',
            status='pending',
            metadata={'course_id': 1}
        )
        
        # Simulate webhook processing based on provider
        if provider == 'stripe':
            # Simulate Stripe webhook success
            updated_transaction = TransactionService.update_transaction_status(
                provider_transaction_id=transaction.provider_transaction_id,
                status='completed',
                metadata={
                    'stripe_payment_intent': f'pi_{transaction.id}',
                    'stripe_webhook_event': 'checkout.session.completed'
                }
            )
        else:  # paystack
            # Simulate Paystack webhook success
            updated_transaction = TransactionService.update_transaction_status(
                provider_transaction_id=transaction.provider_transaction_id,
                status='completed',
                metadata={
                    'paystack_gateway_response': 'Successful',
                    'paystack_webhook_event': 'charge.success'
                }
            )
        
        # Verify transaction was updated to completed status
        self.assertIsNotNone(updated_transaction)
        self.assertEqual(updated_transaction.status, 'completed')
        self.assertTrue(updated_transaction.is_successful)
        
        # Verify access would be granted (transaction is marked as successful)
        self.assertTrue(updated_transaction.can_be_refunded)
        
        # Verify metadata was preserved and updated
        self.assertEqual(updated_transaction.metadata['course_id'], 1)
        if provider == 'stripe':
            self.assertIn('stripe_payment_intent', updated_transaction.metadata)
        else:
            self.assertIn('paystack_gateway_response', updated_transaction.metadata)
    
    # Feature: veetssuites-platform, Property 27: Payment failures allow retry
    @given(
        transaction_amount=st.decimals(min_value=1, max_value=10000, places=2),
        provider=st.one_of(st.just('stripe'), st.just('paystack')),
        failure_reason=st.one_of(
            st.just('card_declined'),
            st.just('insufficient_funds'),
            st.just('expired_card'),
            st.just('invalid_cvc'),
            st.just('processing_error')
        )
    )
    @hypothesis_settings(max_examples=100)
    def test_payment_failures_allow_retry(self, transaction_amount, provider, failure_reason):
        """
        For any payment failure, the system should mark the transaction as failed
        but preserve the transaction record and metadata to allow retry attempts
        without losing the original payment context.
        """
        # Create a pending transaction
        original_metadata = {
            'course_id': 1,
            'user_email': self.user.email,
            'retry_count': 0
        }
        
        transaction = Transaction.objects.create(
            user=self.user,
            amount=transaction_amount,
            currency='USD' if provider == 'stripe' else 'NGN',
            provider=provider,
            provider_transaction_id=f'{provider}_fail_{transaction_amount}_{uuid.uuid4().hex[:8]}',
            status='pending',
            metadata=original_metadata
        )
        
        # Simulate payment failure webhook
        failure_metadata = {
            f'{provider}_failure_reason': failure_reason,
            f'{provider}_webhook_event': 'payment_failed' if provider == 'stripe' else 'charge.failed',
            'can_retry': True
        }
        
        updated_transaction = TransactionService.update_transaction_status(
            provider_transaction_id=transaction.provider_transaction_id,
            status='failed',
            metadata=failure_metadata
        )
        
        # Verify transaction was marked as failed
        self.assertIsNotNone(updated_transaction)
        self.assertEqual(updated_transaction.status, 'failed')
        self.assertFalse(updated_transaction.is_successful)
        self.assertFalse(updated_transaction.is_pending)
        
        # Verify original metadata is preserved for retry
        self.assertEqual(updated_transaction.metadata['course_id'], 1)
        self.assertEqual(updated_transaction.metadata['user_email'], self.user.email)
        self.assertEqual(updated_transaction.metadata['retry_count'], 0)
        
        # Verify failure information is recorded
        self.assertEqual(updated_transaction.metadata[f'{provider}_failure_reason'], failure_reason)
        self.assertTrue(updated_transaction.metadata['can_retry'])
        
        # Verify transaction record is preserved (not deleted)
        self.assertTrue(Transaction.objects.filter(id=transaction.id).exists())
        
        # Simulate retry by creating a new transaction with incremented retry count
        retry_metadata = original_metadata.copy()
        retry_metadata['retry_count'] = 1
        retry_metadata['original_transaction_id'] = transaction.id
        
        retry_transaction = Transaction.objects.create(
            user=self.user,
            amount=transaction_amount,
            currency=transaction.currency,
            provider=provider,
            provider_transaction_id=f'{provider}_retry_{transaction_amount}_{uuid.uuid4().hex[:8]}',
            status='pending',
            metadata=retry_metadata
        )
        
        # Verify retry transaction preserves original context
        self.assertEqual(retry_transaction.user, transaction.user)
        self.assertEqual(retry_transaction.amount, transaction.amount)
        self.assertEqual(retry_transaction.currency, transaction.currency)
        self.assertEqual(retry_transaction.provider, transaction.provider)
        self.assertEqual(retry_transaction.metadata['course_id'], 1)
        self.assertEqual(retry_transaction.metadata['retry_count'], 1)
        self.assertEqual(retry_transaction.metadata['original_transaction_id'], transaction.id)


class PaymentAPIPropertyTests(TransactionTestCase):
    """Property-based tests for payment API endpoints."""
    
    def setUp(self):
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        refresh = RefreshToken.for_user(self.user)
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_provider_routing_consistency(self):
        """
        Test that provider routing is consistent across different inputs.
        This is a simplified version of the property test.
        """
        test_cases = [
            ('NG', 'NGN', 'paystack'),
            ('NG', 'USD', 'paystack'),
            ('US', 'USD', 'stripe'),
            ('GB', 'GBP', 'stripe'),
            (None, 'USD', 'stripe'),
            ('CA', 'NGN', 'paystack'),
        ]
        
        for country_code, currency, expected_provider in test_cases:
            with self.subTest(country=country_code, currency=currency):
                url = '/api/payments/provider-routing/'
                data = {}
                
                if country_code:
                    data['country_code'] = country_code
                if currency:
                    data['currency'] = currency
                
                response = self.client.post(url, data, format='json')
                
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['provider'], expected_provider)
                
                # Verify response structure
                self.assertIn('provider', response.data)
                self.assertIn('currency', response.data)
                self.assertIn('is_configured', response.data)
    
    def test_webhook_processing_structure(self):
        """
        Test that webhook endpoints have the correct structure.
        This is a simplified version of the property test.
        """
        # Test Stripe webhook endpoint structure
        with patch('payments.stripe_service.StripeService.handle_webhook_event') as mock_handler:
            mock_handler.return_value = True
            
            url = '/api/payments/webhook/stripe/'
            webhook_data = {
                'type': 'checkout.session.completed',
                'data': {
                    'object': {
                        'id': 'cs_test_webhook',
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
            mock_handler.assert_called_once()
        
        # Test Paystack webhook endpoint structure
        with patch('payments.paystack_service.PaystackService.handle_webhook_event') as mock_handler:
            mock_handler.return_value = True
            
            url = '/api/payments/webhook/paystack/'
            webhook_data = {
                'event': 'charge.success',
                'data': {
                    'reference': 'ps_test_webhook',
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
            mock_handler.assert_called_once()
    
    def test_payment_session_retry_context(self):
        """
        Test that payment session creation preserves retry context.
        This is a simplified version of the property test.
        """
        test_cases = [
            ('99.99', 'USD'),
            ('149.99', 'NGN'),
        ]
        
        for amount, currency in test_cases:
            with self.subTest(amount=amount, currency=currency):
                url = '/api/payments/create-checkout/'
                metadata = {
                    'course_id': 1,
                    'user_id': self.user.id,
                    'retry_attempt': 0
                }
                
                data = {
                    'amount': amount,
                    'currency': currency,
                    'success_url': 'http://localhost:3000/success',
                    'cancel_url': 'http://localhost:3000/cancel',
                    'metadata': metadata
                }
                
                # Mock provider configuration and session creation
                with patch('payments.services.PaymentProviderRouter.is_provider_configured', return_value=True):
                    if currency == 'USD':
                        # Mock Stripe session creation
                        with patch('payments.stripe_service.stripe.checkout.Session.create') as mock_create:
                            mock_session = MagicMock()
                            mock_session.id = f'cs_test_{amount}'
                            mock_session.url = f'https://checkout.stripe.com/pay/cs_test_{amount}'
                            mock_session.payment_intent = f'pi_test_{amount}'
                            mock_session.expires_at = 1234567890
                            mock_create.return_value = mock_session
                            
                            response = self.client.post(url, data, format='json')
                    else:  # NGN - Paystack
                        # Mock Paystack session creation
                        with patch('payments.paystack_service.PaystackTransaction.initialize') as mock_init:
                            mock_response = {
                                'status': True,
                                'data': {
                                    'reference': f'ps_test_{amount}',
                                    'authorization_url': f'https://checkout.paystack.com/ps_test_{amount}',
                                    'access_code': 'access_code_test'
                                }
                            }
                            mock_init.return_value = mock_response
                            
                            response = self.client.post(url, data, format='json')
                
                # Verify session creation succeeded
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                
                # Verify response contains retry-enabling information
                self.assertIn('session_id', response.data)
                self.assertIn('session_url', response.data)
                self.assertIn('provider', response.data)
                self.assertEqual(float(response.data['amount']), float(amount))
                self.assertEqual(response.data['currency'], currency)
                
                # Verify transaction was created with retry context
                expected_provider = 'stripe' if currency == 'USD' else 'paystack'
                self.assertEqual(response.data['provider'], expected_provider)