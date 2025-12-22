"""
Paystack payment service integration.
"""
import logging
import hashlib
import hmac
from typing import Dict, Any, Optional
from django.conf import settings
from django.contrib.auth import get_user_model
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction as PaystackTransaction

from .models import Transaction
from .services import TransactionService

User = get_user_model()
logger = logging.getLogger(__name__)

# Configure Paystack
paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)


class PaystackService:
    """Service for handling Paystack payment operations."""
    
    @staticmethod
    def create_checkout_session(
        user: User,
        amount: float,
        currency: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Paystack payment initialization.
        
        Args:
            user: User making the payment
            amount: Payment amount
            currency: Currency code (NGN)
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancellation
            metadata: Additional session metadata
            
        Returns:
            Dictionary with payment details
        """
        try:
            # Convert amount to kobo for Paystack (NGN smallest unit)
            amount_kobo = int(amount * 100)
            
            # Prepare metadata
            payment_metadata = {
                'user_id': str(user.id),
                'user_email': user.email,
                'success_url': success_url,
                'cancel_url': cancel_url,
            }
            if metadata:
                payment_metadata.update(metadata)
            
            # Initialize Paystack transaction
            response = PaystackTransaction.initialize(
                email=user.email,
                amount=amount_kobo,
                currency=currency.upper(),
                callback_url=success_url,
                metadata=payment_metadata,
                channels=['card', 'bank', 'ussd', 'qr', 'mobile_money', 'bank_transfer']
            )
            
            if response['status']:
                payment_data = response['data']
                reference = payment_data['reference']
                authorization_url = payment_data['authorization_url']
                
                # Create transaction record
                transaction = TransactionService.create_transaction(
                    user=user,
                    amount=amount,
                    currency=currency,
                    provider='paystack',
                    provider_transaction_id=reference,
                    metadata={
                        'paystack_reference': reference,
                        'paystack_access_code': payment_data.get('access_code'),
                        **payment_metadata
                    }
                )
                
                logger.info(f"Created Paystack payment {reference} for user {user.id}")
                
                return {
                    'session_id': reference,
                    'session_url': authorization_url,
                    'transaction_id': transaction.id,
                    'provider': 'paystack',
                    'amount': amount,
                    'currency': currency,
                    'reference': reference,
                }
            else:
                error_message = response.get('message', 'Unknown error')
                logger.error(f"Paystack initialization failed: {error_message}")
                raise ValueError(f"Failed to initialize payment: {error_message}")
                
        except Exception as e:
            logger.error(f"Error creating Paystack payment: {str(e)}")
            raise ValueError(f"Payment initialization failed: {str(e)}")
    
    @staticmethod
    def handle_webhook_event(event_data: bytes, signature: str) -> bool:
        """
        Handle Paystack webhook events.
        
        Args:
            event_data: Webhook event data as bytes
            signature: Paystack signature for verification
            
        Returns:
            True if event was processed successfully
        """
        try:
            # Verify webhook signature
            if not PaystackService._verify_webhook_signature(event_data, signature):
                logger.error("Paystack webhook signature verification failed")
                return False
            
            # Parse event data
            import json
            event = json.loads(event_data.decode('utf-8'))
            event_type = event.get('event')
            event_object = event.get('data', {})
            
            logger.info(f"Processing Paystack webhook event: {event_type}")
            
            if event_type == 'charge.success':
                return PaystackService._handle_charge_success(event_object)
            elif event_type == 'charge.failed':
                return PaystackService._handle_charge_failed(event_object)
            elif event_type == 'transfer.success':
                return PaystackService._handle_transfer_success(event_object)
            elif event_type == 'transfer.failed':
                return PaystackService._handle_transfer_failed(event_object)
            else:
                logger.info(f"Unhandled Paystack webhook event type: {event_type}")
                return True  # Return True for unhandled but valid events
                
        except Exception as e:
            logger.error(f"Error processing Paystack webhook: {str(e)}")
            return False
    
    @staticmethod
    def _verify_webhook_signature(payload: bytes, signature: str) -> bool:
        """Verify Paystack webhook signature."""
        try:
            # Paystack sends signature in the format: sha512=<hash>
            if not signature.startswith('sha512='):
                return False
            
            expected_signature = signature[7:]  # Remove 'sha512=' prefix
            
            # Create HMAC hash
            computed_signature = hmac.new(
                settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
                payload,
                hashlib.sha512
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, computed_signature)
            
        except Exception as e:
            logger.error(f"Error verifying Paystack webhook signature: {str(e)}")
            return False
    
    @staticmethod
    def _handle_charge_success(charge_object: Dict[str, Any]) -> bool:
        """Handle successful charge."""
        try:
            reference = charge_object.get('reference')
            status = charge_object.get('status')
            
            if status == 'success':
                # Update transaction status
                transaction = TransactionService.update_transaction_status(
                    provider_transaction_id=reference,
                    status='completed',
                    metadata={
                        'paystack_status': status,
                        'paystack_gateway_response': charge_object.get('gateway_response'),
                        'paystack_paid_at': charge_object.get('paid_at'),
                        'paystack_channel': charge_object.get('channel'),
                        'paystack_fees': charge_object.get('fees'),
                    }
                )
                
                if transaction:
                    logger.info(f"Paystack charge succeeded for transaction {transaction.id}")
                    # Trigger course enrollment completion
                    PaystackService._complete_course_enrollment(transaction, charge_object)
                    return True
                else:
                    logger.error(f"Transaction not found for Paystack reference {reference}")
                    return False
            else:
                logger.warning(f"Paystack charge {reference} not successful: {status}")
                return True
                
        except Exception as e:
            logger.error(f"Error handling Paystack charge success: {str(e)}")
            return False
    
    @staticmethod
    def _handle_charge_failed(charge_object: Dict[str, Any]) -> bool:
        """Handle failed charge."""
        try:
            reference = charge_object.get('reference')
            status = charge_object.get('status')
            gateway_response = charge_object.get('gateway_response', 'Payment failed')
            
            # Update transaction status
            transaction = TransactionService.update_transaction_status(
                provider_transaction_id=reference,
                status='failed',
                metadata={
                    'paystack_status': status,
                    'paystack_gateway_response': gateway_response,
                    'paystack_failure_reason': gateway_response,
                    'paystack_channel': charge_object.get('channel'),
                }
            )
            
            if transaction:
                logger.info(f"Paystack charge failed for transaction {transaction.id}: {gateway_response}")
            else:
                logger.error(f"Transaction not found for Paystack reference {reference}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling Paystack charge failure: {str(e)}")
            return False
    
    @staticmethod
    def _handle_transfer_success(transfer_object: Dict[str, Any]) -> bool:
        """Handle successful transfer (for refunds)."""
        try:
            transfer_code = transfer_object.get('transfer_code')
            logger.info(f"Paystack transfer succeeded: {transfer_code}")
            # Handle refund success logic here if needed
            return True
            
        except Exception as e:
            logger.error(f"Error handling Paystack transfer success: {str(e)}")
            return False
    
    @staticmethod
    def _handle_transfer_failed(transfer_object: Dict[str, Any]) -> bool:
        """Handle failed transfer (for refunds)."""
        try:
            transfer_code = transfer_object.get('transfer_code')
            failure_reason = transfer_object.get('failure_reason', 'Unknown error')
            logger.info(f"Paystack transfer failed: {transfer_code} - {failure_reason}")
            # Handle refund failure logic here if needed
            return True
            
        except Exception as e:
            logger.error(f"Error handling Paystack transfer failure: {str(e)}")
            return False
    
    @staticmethod
    def verify_transaction(reference: str) -> Optional[Dict[str, Any]]:
        """
        Verify a Paystack transaction.
        
        Args:
            reference: Paystack transaction reference
            
        Returns:
            Transaction data or None if not found
        """
        try:
            response = PaystackTransaction.verify(reference=reference)
            
            if response['status']:
                data = response['data']
                return {
                    'reference': data.get('reference'),
                    'status': data.get('status'),
                    'amount': data.get('amount'),
                    'currency': data.get('currency'),
                    'channel': data.get('channel'),
                    'fees': data.get('fees'),
                    'gateway_response': data.get('gateway_response'),
                    'paid_at': data.get('paid_at'),
                    'created_at': data.get('created_at'),
                    'metadata': data.get('metadata', {}),
                }
            else:
                logger.error(f"Failed to verify Paystack transaction {reference}: {response.get('message')}")
                return None
                
        except Exception as e:
            logger.error(f"Error verifying Paystack transaction {reference}: {str(e)}")
            return None
    
    @staticmethod
    def create_refund(transaction_reference: str, amount: Optional[int] = None, reason: str = 'requested_by_customer') -> Dict[str, Any]:
        """
        Create a refund for a Paystack transaction.
        
        Args:
            transaction_reference: Paystack transaction reference
            amount: Amount to refund in kobo (None for full refund)
            reason: Reason for refund
            
        Returns:
            Refund details
        """
        try:
            # First verify the transaction
            transaction_data = PaystackService.verify_transaction(transaction_reference)
            if not transaction_data or transaction_data['status'] != 'success':
                raise ValueError("Transaction not found or not successful")
            
            # Paystack doesn't have a direct refund API, so we use transfers
            # This is a simplified implementation - in production you'd need to:
            # 1. Create a transfer recipient for the customer
            # 2. Initiate a transfer to refund the amount
            
            refund_amount = amount or transaction_data['amount']
            
            logger.info(f"Refund requested for Paystack transaction {transaction_reference}: {refund_amount} kobo")
            
            # For now, return a mock response
            # In production, implement actual transfer logic
            return {
                'refund_id': f"rf_{transaction_reference}",
                'amount': refund_amount,
                'currency': transaction_data['currency'],
                'status': 'pending',
                'reason': reason,
                'created_at': transaction_data['created_at'],
            }
            
        except Exception as e:
            logger.error(f"Error creating Paystack refund: {str(e)}")
            raise ValueError(f"Failed to create refund: {str(e)}")
    
    @staticmethod
    def get_payment_channels() -> list:
        """Get available Paystack payment channels."""
        return ['card', 'bank', 'ussd', 'qr', 'mobile_money', 'bank_transfer']
    
    @staticmethod
    def get_supported_currencies() -> list:
        """Get currencies supported by Paystack."""
        return ['NGN', 'USD', 'GHS', 'ZAR', 'KES']
    
    @staticmethod
    def _complete_course_enrollment(transaction: 'Transaction', charge_object: Dict[str, Any]) -> None:
        """
        Complete course enrollment after successful payment.
        
        Args:
            transaction: Transaction instance
            charge_object: Paystack charge object
        """
        try:
            # Get enrollment ID from transaction metadata
            enrollment_id = transaction.metadata.get('enrollment_id')
            if not enrollment_id:
                logger.warning(f"No enrollment_id in transaction {transaction.id} metadata")
                return
            
            # Import here to avoid circular imports
            from hub3660.models import Enrollment
            from hub3660.views import _register_student_for_course_sessions
            
            try:
                enrollment = Enrollment.objects.get(id=enrollment_id)
                
                # Complete the enrollment
                enrollment.complete_payment(transaction.provider_transaction_id)
                logger.info(f"Completed enrollment {enrollment.id} for user {enrollment.student.email}")
                
                # Register student for all upcoming Zoom sessions
                _register_student_for_course_sessions(enrollment.student, enrollment.course)
                
            except Enrollment.DoesNotExist:
                logger.error(f"Enrollment {enrollment_id} not found for transaction {transaction.id}")
                
        except Exception as e:
            logger.error(f"Error completing course enrollment for transaction {transaction.id}: {e}")