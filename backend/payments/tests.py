"""
Tests for payments app.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Transaction
from .services import PaymentProviderRouter, TransactionService, PaymentSessionService

User = get_user_model()


class TransactionModelTest(TestCase):
    """Test Transaction model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_create_transaction(self):
        """Test creating a transaction."""
        transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('99.99'),
            currency='USD',
            provider='stripe',
            provider_transaction_id='stripe_123456',
            status='pending'
        )
        
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal('99.99'))
        self.assertEqual(transaction.currency, 'USD')
        self.assertEqual(transaction.provider, 'stripe')
        self.assertEqual(transaction.status, 'pending')
        self.assertTrue(transaction.is_pending)
        self.assertFalse(transaction.is_successful)
    
    def test_transaction_properties(self):
        """Test transaction properties."""
        transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            currency='USD',
            provider='paystack',
            provider_transaction_id='paystack_789',
            status='completed'
        )
        
        self.assertTrue(transaction.is_successful)
        self.assertFalse(transaction.is_pending)
        self.assertTrue(transaction.can_be_refunded)


class PaymentProviderRouterTest(TestCase):
    """Test PaymentProviderRouter service."""
    
    def test_nigerian_routing(self):
        """Test routing for Nigerian users."""
        provider = PaymentProviderRouter.get_provider('NG', 'NGN')
        self.assertEqual(provider, 'paystack')
        
        provider = PaymentProviderRouter.get_provider('NG', 'USD')
        self.assertEqual(provider, 'paystack')
    
    def test_global_routing(self):
        """Test routing for non-Nigerian users."""
        provider = PaymentProviderRouter.get_provider('US', 'USD')
        self.assertEqual(provider, 'stripe')
        
        provider = PaymentProviderRouter.get_provider('GB', 'GBP')
        self.assertEqual(provider, 'stripe')
        
        provider = PaymentProviderRouter.get_provider(None, 'USD')
        self.assertEqual(provider, 'stripe')
    
    def test_ngn_currency_routing(self):
        """Test routing based on NGN currency."""
        provider = PaymentProviderRouter.get_provider('US', 'NGN')
        self.assertEqual(provider, 'paystack')


class TransactionServiceTest(TestCase):
    """Test TransactionService."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_create_transaction(self):
        """Test creating transaction via service."""
        transaction = TransactionService.create_transaction(
            user=self.user,
            amount=75.50,
            currency='USD',
            provider='stripe',
            provider_transaction_id='stripe_test_123',
            metadata={'course_id': 1}
        )
        
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal('75.50'))
        self.assertEqual(transaction.status, 'pending')
        self.assertEqual(transaction.metadata['course_id'], 1)
    
    def test_update_transaction_status(self):
        """Test updating transaction status."""
        transaction = TransactionService.create_transaction(
            user=self.user,
            amount=100.00,
            currency='USD',
            provider='stripe',
            provider_transaction_id='stripe_update_test'
        )
        
        updated = TransactionService.update_transaction_status(
            provider_transaction_id='stripe_update_test',
            status='completed',
            metadata={'payment_intent': 'pi_123'}
        )
        
        self.assertEqual(updated.status, 'completed')
        self.assertEqual(updated.metadata['payment_intent'], 'pi_123')
    
    def test_get_user_transactions(self):
        """Test getting user transactions."""
        # Create multiple transactions
        TransactionService.create_transaction(
            user=self.user,
            amount=50.00,
            currency='USD',
            provider='stripe',
            provider_transaction_id='stripe_1'
        )
        
        TransactionService.create_transaction(
            user=self.user,
            amount=75.00,
            currency='USD',
            provider='paystack',
            provider_transaction_id='paystack_1'
        )
        
        transactions = TransactionService.get_user_transactions(self.user)
        self.assertEqual(len(transactions), 2)
        
        # Test status filtering
        TransactionService.update_transaction_status('stripe_1', 'completed')
        completed_transactions = TransactionService.get_user_transactions(
            self.user, status='completed'
        )
        self.assertEqual(len(completed_transactions), 1)


class PaymentAPITest(APITestCase):
    """Test payment API endpoints."""
    
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
    
    def test_provider_routing_endpoint(self):
        """Test provider routing endpoint."""
        url = '/api/payments/provider-routing/'
        data = {
            'country_code': 'NG',
            'currency': 'NGN'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['provider'], 'paystack')
        self.assertEqual(response.data['country_code'], 'NG')
        self.assertEqual(response.data['currency'], 'NGN')
    
    def test_create_payment_session(self):
        """Test creating payment session."""
        from unittest.mock import patch, MagicMock
        
        url = '/api/payments/create-checkout/'
        data = {
            'amount': '99.99',
            'currency': 'USD',
            'success_url': 'http://localhost:3000/success',
            'cancel_url': 'http://localhost:3000/cancel',
            'metadata': {'course_id': 1}
        }
        
        # Mock the provider configuration check and Stripe service
        with patch('payments.services.PaymentProviderRouter.is_provider_configured', return_value=True), \
             patch('payments.stripe_service.stripe.checkout.Session.create') as mock_stripe_create:
            
            # Mock Stripe session creation
            mock_session = MagicMock()
            mock_session.id = 'cs_test_mock'
            mock_session.url = 'https://checkout.stripe.com/pay/cs_test_mock'
            mock_session.payment_intent = 'pi_test_mock'
            mock_session.expires_at = 1234567890
            mock_stripe_create.return_value = mock_session
            
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['provider'], 'stripe')
            self.assertEqual(float(response.data['amount']), 99.99)
            self.assertEqual(response.data['currency'], 'USD')
    
    def test_transaction_list(self):
        """Test getting transaction list."""
        # Create a transaction
        Transaction.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            currency='USD',
            provider='stripe',
            provider_transaction_id='test_123',
            status='completed'
        )
        
        url = '/api/payments/transactions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount'], '50.00')
    
    def test_transaction_detail(self):
        """Test getting transaction detail."""
        transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('75.00'),
            currency='USD',
            provider='stripe',
            provider_transaction_id='detail_test',
            status='pending'
        )
        
        url = f'/api/payments/transactions/{transaction.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], '75.00')
        self.assertEqual(response.data['status'], 'pending')
    
    def test_payment_status(self):
        """Test payment status endpoint."""
        transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('100.00'),
            currency='USD',
            provider='stripe',
            provider_transaction_id='status_test',
            status='completed'
        )
        
        url = f'/api/payments/transactions/{transaction.id}/status/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['transaction_id'], transaction.id)