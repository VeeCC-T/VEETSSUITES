"""
Stripe payment service integration.
"""
import logging
import stripe
import time
from typing import Dict, Any, Optional
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Transaction
from .services import TransactionService

User = get_user_model()
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for handling Stripe payment operations."""
    
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
        Create a Stripe checkout session.
        
        Args:
            user: User making the payment
            amount: Payment amount
            currency: Currency code
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancellation
            metadata: Additional session metadata
            
        Returns:
            Dictionary with session details
        """
        try:
            # Convert amount to cents for Stripe
            amount_cents = int(amount * 100)
            
            # Prepare metadata
            session_metadata = {
                'user_id': str(user.id),
                'user_email': user.email,
            }
            if metadata:
                session_metadata.update(metadata)
            
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {
                            'name': f'Course Enrollment - {user.email}',
                            'description': 'VEETSSUITES Course Access',
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user.email,
                metadata=session_metadata,
                expires_at=int(time.time() + 1800)  # 30 minutes from now
            )
            
            # Create transaction record
            transaction = TransactionService.create_transaction(
                user=user,
                amount=amount,
                currency=currency,
                provider='stripe',
                provider_transaction_id=session.id,
                metadata={
                    'stripe_session_id': session.id,
                    'stripe_payment_intent': session.payment_intent,
                    **session_metadata
                }
            )
            
            logger.info(f"Created Stripe checkout session {session.id} for user {user.id}")
            
            return {
                'session_id': session.id,
                'session_url': session.url,
                'transaction_id': transaction.id,
                'provider': 'stripe',
                'amount': amount,
                'currency': currency,
                'expires_at': session.expires_at,
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {str(e)}")
            raise ValueError(f"Failed to create payment session: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating Stripe checkout session: {str(e)}")
            raise ValueError(f"Payment session creation failed: {str(e)}")
    
    @staticmethod
    def handle_webhook_event(event_data: Dict[str, Any], signature: str) -> bool:
        """
        Handle Stripe webhook events.
        
        Args:
            event_data: Webhook event data
            signature: Stripe signature for verification
            
        Returns:
            True if event was processed successfully
        """
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload=event_data,
                sig_header=signature,
                secret=settings.STRIPE_WEBHOOK_SECRET
            )
            
            event_type = event['type']
            event_object = event['data']['object']
            
            logger.info(f"Processing Stripe webhook event: {event_type}")
            
            if event_type == 'checkout.session.completed':
                return StripeService._handle_checkout_completed(event_object)
            elif event_type == 'payment_intent.succeeded':
                return StripeService._handle_payment_succeeded(event_object)
            elif event_type == 'payment_intent.payment_failed':
                return StripeService._handle_payment_failed(event_object)
            elif event_type == 'invoice.payment_succeeded':
                return StripeService._handle_invoice_payment_succeeded(event_object)
            else:
                logger.info(f"Unhandled Stripe webhook event type: {event_type}")
                return True  # Return True for unhandled but valid events
                
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Stripe webhook signature verification failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {str(e)}")
            return False
    
    @staticmethod
    def _handle_checkout_completed(session_object: Dict[str, Any]) -> bool:
        """Handle successful checkout session completion."""
        try:
            session_id = session_object['id']
            payment_status = session_object['payment_status']
            
            if payment_status == 'paid':
                # Update transaction status
                transaction = TransactionService.update_transaction_status(
                    provider_transaction_id=session_id,
                    status='completed',
                    metadata={
                        'stripe_payment_status': payment_status,
                        'stripe_payment_intent': session_object.get('payment_intent'),
                        'stripe_customer': session_object.get('customer'),
                        'completed_at': session_object.get('created'),
                    }
                )
                
                if transaction:
                    logger.info(f"Stripe checkout completed for transaction {transaction.id}")
                    # Trigger course enrollment completion
                    StripeService._complete_course_enrollment(transaction, session_object)
                    return True
                else:
                    logger.error(f"Transaction not found for Stripe session {session_id}")
                    return False
            else:
                logger.warning(f"Stripe checkout session {session_id} not paid: {payment_status}")
                return True
                
        except Exception as e:
            logger.error(f"Error handling Stripe checkout completion: {str(e)}")
            return False
    
    @staticmethod
    def _handle_payment_succeeded(payment_intent_object: Dict[str, Any]) -> bool:
        """Handle successful payment intent."""
        try:
            payment_intent_id = payment_intent_object['id']
            
            # Find transaction by payment intent ID
            transactions = Transaction.objects.filter(
                provider='stripe',
                metadata__stripe_payment_intent=payment_intent_id
            )
            
            for transaction in transactions:
                TransactionService.update_transaction_status(
                    provider_transaction_id=transaction.provider_transaction_id,
                    status='completed',
                    metadata={
                        'stripe_payment_intent_status': payment_intent_object.get('status'),
                        'stripe_amount_received': payment_intent_object.get('amount_received'),
                        'payment_succeeded_at': payment_intent_object.get('created'),
                    }
                )
                
            logger.info(f"Stripe payment intent succeeded: {payment_intent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling Stripe payment success: {str(e)}")
            return False
    
    @staticmethod
    def _handle_payment_failed(payment_intent_object: Dict[str, Any]) -> bool:
        """Handle failed payment intent."""
        try:
            payment_intent_id = payment_intent_object['id']
            failure_reason = payment_intent_object.get('last_payment_error', {}).get('message', 'Unknown error')
            
            # Find transaction by payment intent ID
            transactions = Transaction.objects.filter(
                provider='stripe',
                metadata__stripe_payment_intent=payment_intent_id
            )
            
            for transaction in transactions:
                TransactionService.update_transaction_status(
                    provider_transaction_id=transaction.provider_transaction_id,
                    status='failed',
                    metadata={
                        'stripe_payment_intent_status': payment_intent_object.get('status'),
                        'stripe_failure_reason': failure_reason,
                        'payment_failed_at': payment_intent_object.get('created'),
                    }
                )
                
            logger.info(f"Stripe payment intent failed: {payment_intent_id} - {failure_reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling Stripe payment failure: {str(e)}")
            return False
    
    @staticmethod
    def _handle_invoice_payment_succeeded(invoice_object: Dict[str, Any]) -> bool:
        """Handle successful invoice payment (for subscriptions)."""
        try:
            invoice_id = invoice_object['id']
            subscription_id = invoice_object.get('subscription')
            
            logger.info(f"Stripe invoice payment succeeded: {invoice_id} for subscription {subscription_id}")
            # Handle subscription-related logic here if needed
            return True
            
        except Exception as e:
            logger.error(f"Error handling Stripe invoice payment: {str(e)}")
            return False
    
    @staticmethod
    def retrieve_session(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a Stripe checkout session.
        
        Args:
            session_id: Stripe session ID
            
        Returns:
            Session data or None if not found
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                'id': session.id,
                'payment_status': session.payment_status,
                'payment_intent': session.payment_intent,
                'customer': session.customer,
                'amount_total': session.amount_total,
                'currency': session.currency,
                'metadata': session.metadata,
                'created': session.created,
                'expires_at': session.expires_at,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving Stripe session {session_id}: {str(e)}")
            return None
    
    @staticmethod
    def create_refund(payment_intent_id: str, amount: Optional[int] = None, reason: str = 'requested_by_customer') -> Dict[str, Any]:
        """
        Create a refund for a payment.
        
        Args:
            payment_intent_id: Stripe payment intent ID
            amount: Amount to refund in cents (None for full refund)
            reason: Reason for refund
            
        Returns:
            Refund details
        """
        try:
            refund_data = {
                'payment_intent': payment_intent_id,
                'reason': reason,
            }
            
            if amount:
                refund_data['amount'] = amount
            
            refund = stripe.Refund.create(**refund_data)
            
            logger.info(f"Created Stripe refund {refund.id} for payment intent {payment_intent_id}")
            
            return {
                'refund_id': refund.id,
                'amount': refund.amount,
                'currency': refund.currency,
                'status': refund.status,
                'reason': refund.reason,
                'created': refund.created,
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe refund: {str(e)}")
            raise ValueError(f"Failed to create refund: {str(e)}")
    
    @staticmethod
    def _complete_course_enrollment(transaction: 'Transaction', session_object: Dict[str, Any]) -> None:
        """
        Complete course enrollment after successful payment.
        
        Args:
            transaction: Transaction instance
            session_object: Stripe session object
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