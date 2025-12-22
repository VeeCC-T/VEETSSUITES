"""
URL configuration for payments app.
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment session management
    path('create-checkout/', views.PaymentSessionCreateView.as_view(), name='create-checkout'),
    path('provider-routing/', views.PaymentProviderRoutingView.as_view(), name='provider-routing'),
    
    # Transaction management
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<int:transaction_id>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/<int:transaction_id>/status/', views.payment_status, name='payment-status'),
    
    # Webhook endpoints
    path('webhook/stripe/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('webhook/paystack/', views.PaystackWebhookView.as_view(), name='paystack-webhook'),
]