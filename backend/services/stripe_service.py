"""
Stripe integration for subscription management
"""

import stripe
from typing import Optional, Dict, Any
from datetime import datetime

from ..core.config import settings

class StripeService:
    """Handle Stripe payment operations"""
    
    def __init__(self):
        self.stripe_secret_key = settings.stripe_secret_key
        if self.stripe_secret_key:
            stripe.api_key = self.stripe_secret_key
    
    def is_configured(self) -> bool:
        """Check if Stripe is configured"""
        return bool(self.stripe_secret_key)
    
    def create_customer(
        self, 
        email: str, 
        name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a Stripe customer"""
        if not self.is_configured():
            raise ValueError("Stripe is not configured")
        
        customer_data = {
            "email": email,
            "metadata": metadata or {}
        }
        
        if name:
            customer_data["name"] = name
        
        customer = stripe.Customer.create(**customer_data)
        return customer
    
    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a subscription"""
        if not self.is_configured():
            raise ValueError("Stripe is not configured")
        
        subscription_data = {
            "customer": customer_id,
            "items": [{"price": price_id}],
            "payment_behavior": "default_incomplete",
            "expand": ["latest_invoice.payment_intent"],
            "metadata": metadata or {}
        }
        
        subscription = stripe.Subscription.create(**subscription_data)
        return subscription
    
    def cancel_subscription(
        self,
        subscription_id: str,
        cancel_at_period_end: bool = False
    ) -> Dict[str, Any]:
        """Cancel a subscription"""
        if not self.is_configured():
            raise ValueError("Stripe is not configured")
        
        if cancel_at_period_end:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
        else:
            subscription = stripe.Subscription.delete(subscription_id)
        
        return subscription
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription details"""
        if not self.is_configured():
            raise ValueError("Stripe is not configured")
        
        subscription = stripe.Subscription.retrieve(subscription_id)
        return subscription
    
    def update_subscription_tier(
        self,
        subscription_id: str,
        new_price_id: str
    ) -> Dict[str, Any]:
        """Update subscription to new tier"""
        if not self.is_configured():
            raise ValueError("Stripe is not configured")
        
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Update subscription
        updated_subscription = stripe.Subscription.modify(
            subscription_id,
            items=[{
                "id": subscription["items"]["data"][0].id,
                "price": new_price_id,
            }],
            proration_behavior="create_prorations"
        )
        
        return updated_subscription
    
    def create_checkout_session(
        self,
        customer_id: Optional[str] = None,
        price_id: str = None,
        success_url: str = None,
        cancel_url: str = None,
        mode: str = "subscription",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a checkout session"""
        if not self.is_configured():
            raise ValueError("Stripe is not configured")
        
        session_data = {
            "mode": mode,
            "success_url": success_url or f"{settings.domain}/dashboard?success=true",
            "cancel_url": cancel_url or f"{settings.domain}/pricing?canceled=true",
            "metadata": metadata or {}
        }
        
        if customer_id:
            session_data["customer"] = customer_id
        else:
            session_data["customer_creation"] = "if_required"
        
        if price_id:
            session_data["line_items"] = [{
                "price": price_id,
                "quantity": 1
            }]
        
        session = stripe.checkout.Session.create(**session_data)
        return session
    
    def create_portal_session(
        self,
        customer_id: str,
        return_url: str = None
    ) -> Dict[str, Any]:
        """Create customer portal session"""
        if not self.is_configured():
            raise ValueError("Stripe is not configured")
        
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url or f"{settings.domain}/dashboard"
        )
        return session
    
    def handle_webhook(
        self,
        payload: bytes,
        sig_header: str,
        endpoint_secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        if not self.is_configured():
            raise ValueError("Stripe is not configured")
        
        webhook_secret = endpoint_secret or settings.stripe_webhook_secret
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            raise ValueError(f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise ValueError(f"Invalid signature: {str(e)}")
        
        return event
    
    def get_price_details(self) -> Dict[str, Dict]:
        """Get pricing details for all tiers"""
        # In production, fetch from Stripe
        # For now, return hardcoded prices
        return {
            "free": {
                "price_id": None,
                "amount": 0,
                "currency": "usd",
                "interval": "month",
                "conversions": 10,
                "ai_questions": 5,
                "features": ["Basic PDF tools", "Community support"]
            },
            "pro": {
                "price_id": "price_pro_monthly",  # Replace with actual Stripe price ID
                "amount": 2900,  # $29.00
                "currency": "usd",
                "interval": "month",
                "conversions": 100,
                "ai_questions": 50,
                "features": ["All PDF tools", "API access", "Priority support"]
            },
            "business": {
                "price_id": "price_business_monthly",  # Replace with actual Stripe price ID
                "amount": 9900,  # $99.00
                "currency": "usd",
                "interval": "month",
                "conversions": 500,
                "ai_questions": 250,
                "features": ["Team collaboration", "White-label", "Dedicated support"]
            },
            "enterprise": {
                "price_id": None,  # Contact sales
                "amount": 29900,  # $299.00
                "currency": "usd",
                "interval": "month",
                "conversions": 2000,
                "ai_questions": 1000,
                "features": ["Custom everything", "SLA", "24/7 support"]
            }
        }
    
    def create_invoice(
        self,
        customer_id: str,
        amount: int,
        currency: str = "usd",
        description: str = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create an invoice for one-time charges"""
        if not self.is_configured():
            raise ValueError("Stripe is not configured")
        
        invoice_item = stripe.InvoiceItem.create(
            customer=customer_id,
            amount=amount,
            currency=currency,
            description=description or "Additional usage",
            metadata=metadata or {}
        )
        
        invoice = stripe.Invoice.create(
            customer=customer_id,
            auto_advance=True,
            metadata=metadata or {}
        )
        
        return invoice
    
    def get_payment_methods(self, customer_id: str) -> list:
        """Get customer's payment methods"""
        if not self.is_configured():
            raise ValueError("Stripe is not configured")
        
        payment_methods = stripe.PaymentMethod.list(
            customer=customer_id,
            type="card"
        )
        
        return payment_methods.data
    
    def update_customer(
        self,
        customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Update customer information"""
        if not self.is_configured():
            raise ValueError("Stripe is not configured")
        
        update_data = {}
        if email:
            update_data["email"] = email
        if name:
            update_data["name"] = name
        if metadata:
            update_data["metadata"] = metadata
        
        customer = stripe.Customer.modify(customer_id, **update_data)
        return customer
    
    def get_invoices(self, customer_id: str, limit: int = 10) -> list:
        """Get customer's invoices"""
        if not self.is_configured():
            raise ValueError("Stripe is not configured")
        
        invoices = stripe.Invoice.list(
            customer=customer_id,
            limit=limit
        )
        
        return invoices.data