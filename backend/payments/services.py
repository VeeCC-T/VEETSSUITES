"""
Payment services for handling different payment providers.
"""
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Transaction

User = get_user_model()
logger = logging.getLogger(__name__)


class PaymentProviderRouter:
    """Service to route payments to appropriate provider based on location and currency."""
    
    # Nigerian payment providers for NGN currency
    NIGERIAN_PROVIDERS = ['paystack', 'flutterwave']
    # Global payment provider
    GLOBAL_PROVIDER = 'stripe'
    
    @classmethod
    def get_provider(cls, country_code: Optional[str] = None, currency: str = 'USD') -> str:
        """
        Determine the appropriate payment provider based on country and currency.
        
        Args:
            country_code: ISO 2-letter country code (e.g., 'NG', 'US')
            currency: Currency code (e.g., 'USD', 'NGN')
            
        Returns:
            Provider name ('stripe', 'paystack', or 'flutterwave')
        """
        # Route Nigerian users or NGN currency to local providers
        if country_code == 'NG' or currency == 'NGN':
            # Prefer Paystack for Nigerian transactions
            return 'paystack'
        
        # Default to Stripe for all other countries/currencies
        return cls.GLOBAL_PROVIDER
    
    @classmethod
    def get_provider_config(cls, provider: str) -> Dict[str, str]:
        """
        Get configuration for a specific payment provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Dictionary with provider configuration
        """
        configs = {
            'stripe': {
                'secret_key': settings.STRIPE_SECRET_KEY,
                'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
                'webhook_secret': settings.STRIPE_WEBHOOK_SECRET,
            },
            'paystack': {
                'secret_key': settings.PAYSTACK_SECRET_KEY,
                'public_key': settings.PAYSTACK_PUBLIC_KEY,
            },
            'flutterwave': {
                # Flutterwave config would go here when implemented
                'secret_key': '',
                'public_key': '',
            }
        }
        
        return configs.get(provider, {})
    
    @classmethod
    def is_provider_configured(cls, provider: str) -> bool:
        """
        Check if a payment provider is properly configured.
        
        Args:
            provider: Provider name
            
        Returns:
            True if provider has required configuration
        """
        config = cls.get_provider_config(provider)
        
        if provider == 'stripe':
            return bool(config.get('secret_key') and config.get('publishable_key'))
        elif provider == 'paystack':
            return bool(config.get('secret_key') and config.get('public_key'))
        elif provider == 'flutterwave':
            return bool(config.get('secret_key') and config.get('public_key'))
        
        return False


class TransactionService:
    """Service for managing transactions."""
    
    @staticmethod
    def create_transaction(
        user: User,
        amount: float,
        currency: str,
        provider: str,
        provider_transaction_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Transaction:
        """
        Create a new transaction record.
        
        Args:
            user: User making the payment
            amount: Payment amount
            currency: Currency code
            provider: Payment provider
            provider_transaction_id: Provider's transaction ID
            metadata: Additional transaction data
            
        Returns:
            Created Transaction instance
        """
        transaction = Transaction.objects.create(
            user=user,
            amount=amount,
            currency=currency,
            provider=provider,
            provider_transaction_id=provider_transaction_id,
            status='pending',
            metadata=metadata or {}
        )
        
        logger.info(f"Created transaction {transaction.id} for user {user.id}")
        return transaction
    
    @staticmethod
    def update_transaction_status(
        provider_transaction_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Transaction]:
        """
        Update transaction status based on provider transaction ID.
        
        Args:
            provider_transaction_id: Provider's transaction ID
            status: New status
            metadata: Additional metadata to merge
            
        Returns:
            Updated Transaction instance or None if not found
        """
        try:
            transaction = Transaction.objects.get(
                provider_transaction_id=provider_transaction_id
            )
            
            transaction.status = status
            if metadata:
                transaction.metadata.update(metadata)
            
            transaction.save()
            
            logger.info(f"Updated transaction {transaction.id} status to {status}")
            return transaction
            
        except Transaction.DoesNotExist:
            logger.error(f"Transaction not found: {provider_transaction_id}")
            return None
    
    @staticmethod
    def get_user_transactions(user: User, status: Optional[str] = None) -> list:
        """
        Get transactions for a specific user.
        
        Args:
            user: User instance
            status: Optional status filter
            
        Returns:
            List of Transaction instances
        """
        queryset = Transaction.objects.filter(user=user)
        
        if status:
            queryset = queryset.filter(status=status)
            
        return list(queryset.order_by('-created_at'))


class PaymentSessionService:
    """Service for creating payment sessions with different providers."""
    
    @staticmethod
    def create_payment_session(
        user: User,
        amount: float,
        currency: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, Any]] = None,
        country_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a payment session with the appropriate provider.
        
        Args:
            user: User making the payment
            amount: Payment amount
            currency: Currency code
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancellation
            metadata: Additional session data
            country_code: User's country code for provider routing
            
        Returns:
            Dictionary with session details and redirect URL
        """
        # Determine the appropriate provider
        provider = PaymentProviderRouter.get_provider(country_code, currency)
        
        # Check if provider is configured
        if not PaymentProviderRouter.is_provider_configured(provider):
            raise ValueError(f"Payment provider {provider} is not configured")
        
        # Create transaction record
        # Note: provider_transaction_id will be updated when actual session is created
        transaction = TransactionService.create_transaction(
            user=user,
            amount=amount,
            currency=currency,
            provider=provider,
            provider_transaction_id=f"temp_{user.id}_{amount}",  # Temporary ID
            metadata=metadata
        )
        
        # Create session with appropriate provider
        if provider == 'stripe':
            from .stripe_service import StripeService
            session_data = StripeService.create_checkout_session(
                user=user,
                amount=amount,
                currency=currency,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata
            )
            return session_data
        elif provider == 'paystack':
            from .paystack_service import PaystackService
            session_data = PaystackService.create_checkout_session(
                user=user,
                amount=amount,
                currency=currency,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata
            )
            return session_data
        else:
            # Default fallback
            return {
                'transaction_id': transaction.id,
                'provider': provider,
                'amount': amount,
                'currency': currency,
                'session_url': None,
                'session_id': None,
            }