import httpx
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseResource:
    """Base class for SDK resources"""

    def __init__(self, client: 'OneRouterClient'):
        self.client = client

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to OneRouter API"""
        url = f"{self.client.base_url}{endpoint}"

        headers = {
            "Authorization": f"Bearer {self.client.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if method == "POST":
                    response = await client.post(url, json=payload, headers=headers)
                elif method == "GET":
                    response = await client.get(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                error_data = e.response.json() if e.response.text else {}
                raise Exception(
                    f"{error_data.get('detail', e.response.text)}"
                )
            except Exception as e:
                raise Exception(f"Request failed: {str(e)}")


class SMSResource(BaseResource):
    """SMS communication resource"""

    async def send(
        self,
        to: str,
        body: str,
        from_number: Optional[str] = None,
        provider: str = "twilio",
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS message

        Args:
            to: Recipient phone number (E.164 format, e.g., +1234567890)
            body: SMS message content (1-1600 characters)
            from_number: Override default from number (optional)
            provider: Service provider (default: twilio)
            idempotency_key: Prevent duplicate requests (optional)

        Returns:
            Dict with message_id, status, service, cost

        Example:
            >>> await client.sms.send(
            ...     to="+1234567890",
            ...     body="Your OTP is 123456. Valid for 10 minutes."
            ... )
            {
                "message_id": "SM123456789",
                "status": "sent",
                "service": "twilio",
                "cost": 0.0079,
                "currency": "USD",
                "created_at": "2025-01-15T10:30:00Z"
            }
        """
        payload = {
            "to": to,
            "body": body,
            "provider": provider
        }

        if from_number:
            payload["from_number"] = from_number
        if idempotency_key:
            payload["idempotency_key"] = idempotency_key

        return await self._make_request("POST", "/sms", payload)

    async def get_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get SMS delivery status

        Args:
            message_id: SMS message ID from send() response

        Returns:
            Dict with message_id, status, provider_data

        Example:
            >>> await client.sms.get_status("SM123456789")
            {
                "message_id": "SM123456789",
                "status": "delivered",
                "service": "twilio",
                "provider_data": {...}
            }
        """
        return await self._make_request("GET", f"/sms/{message_id}")


class EmailResource(BaseResource):
    """Email communication resource"""

    async def send(
        self,
        to: str,
        subject: str,
        html_body: Optional[str] = None,
        text_body: Optional[str] = None,
        from_email: Optional[str] = None,
        provider: str = "resend",
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email message

        Args:
            to: Recipient email address
            subject: Email subject
            html_body: HTML email body (optional)
            text_body: Plain text email body (optional)
            from_email: Override default from email (optional)
            provider: Service provider (default: resend)
            idempotency_key: Prevent duplicate requests (optional)

        Returns:
            Dict with email_id, status, service, cost

        Example:
            >>> await client.email.send(
            ...     to="user@example.com",
            ...     subject="Welcome to Our Platform!",
            ...     html_body="<h1>Welcome!</h1><p>Your account is ready.</p>"
            ... )
            {
                "email_id": "EM123456789",
                "status": "sent",
                "service": "resend",
                "cost": 0.0001,
                "currency": "USD",
                "created_at": "2025-01-15T10:30:00Z"
            }
        """
        if not html_body and not text_body:
            raise ValueError("Either html_body or text_body is required")

        payload = {
            "to": to,
            "subject": subject,
            "provider": provider
        }

        if html_body:
            payload["html_body"] = html_body
        if text_body:
            payload["text_body"] = text_body
        if from_email:
            payload["from_email"] = from_email
        if idempotency_key:
            payload["idempotency_key"] = idempotency_key

        return await self._make_request("POST", "/email", payload)

    async def get_status(self, email_id: str) -> Dict[str, Any]:
        """
        Get email delivery status

        Args:
            email_id: Email ID from send() response

        Returns:
            Dict with email_id, status, created_at, provider_data

        Example:
            >>> await client.email.get_status("EM123456789")
            {
                "email_id": "EM123456789",
                "status": "delivered",
                "service": "resend",
                "created_at": "2025-01-15T10:30:00Z",
                "provider_data": {...}
            }
        """
        return await self._make_request("GET", f"/email/{email_id}")


class OneRouterClient:
    """OneRouter SDK Client for communications"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.onerouter.com"
    ):
        self.api_key = api_key
        self.base_url = base_url

        # Initialize resources
        self.sms = SMSResource(self)
        self.email = EmailResource(self)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def OneRouter(api_key: str, base_url: str = "https://api.onerouter.com"):
    """Factory function to create OneRouter client"""
    return OneRouterClient(api_key, base_url)
