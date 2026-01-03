"""
OneRouter Python SDK
====================
Unified API client for payments, subscriptions, SMS, email, and more.

Installation:
    pip install onerouter

Usage:
    from onerouter import OneRouter

    client = OneRouter(api_key="unf_live_xxx")
    order = client.payments.create(amount=500.00, currency="INR")
    sms = client.sms.send(to="+1234567890", body="Hello!")
    email = client.email.send(to="test@example.com", subject="Test", html_body="<h1>Hi</h1>")
"""

from .client import OneRouter
from .utils import OneRouterSync
from .exceptions import (
    OneRouterError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError
)

__version__ = "2.0.1"
__all__ = [
    "OneRouter",
    "OneRouterSync",
    "OneRouterError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "APIError",
]