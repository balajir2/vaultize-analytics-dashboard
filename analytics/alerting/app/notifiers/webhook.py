"""
Webhook Notifier

Sends HTTP POST notifications to configured webhook endpoints.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from app.models.alert_rule import AlertAction
from app.notifiers.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


@dataclass
class NotificationContext:
    """Context for template variable substitution."""
    name: str
    description: str
    result_count: float
    threshold: float
    timestamp: str
    severity: str
    environment: str
    service: str
    state: str
    operator: str
    p95_response_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class NotificationResult:
    """Result of sending a webhook notification."""
    success: bool
    status_code: Optional[int] = None
    error: Optional[str] = None
    attempts: int = 1


class WebhookNotifier:
    """Sends webhook notifications with retry logic."""

    def __init__(self, timeout: int = 10, retries: int = 3):
        self.timeout = timeout
        self.retries = retries
        self.renderer = TemplateRenderer()

    async def send(self, action: AlertAction, context: NotificationContext) -> NotificationResult:
        """Send a webhook notification with template rendering and retries."""
        rendered_body = self.renderer.render(action.webhook.body, context.to_dict())

        for attempt in range(1, self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=action.webhook.method,
                        url=action.webhook.url,
                        headers=action.webhook.headers,
                        json=rendered_body,
                    )

                if response.status_code < 400:
                    logger.info(
                        f"Webhook '{action.name}' sent successfully "
                        f"(status={response.status_code}, attempt={attempt})"
                    )
                    return NotificationResult(
                        success=True,
                        status_code=response.status_code,
                        attempts=attempt,
                    )

                logger.warning(
                    f"Webhook '{action.name}' returned {response.status_code} "
                    f"(attempt {attempt}/{self.retries})"
                )

            except Exception as e:
                logger.warning(
                    f"Webhook '{action.name}' failed (attempt {attempt}/{self.retries}): {e}"
                )
                if attempt < self.retries:
                    backoff = 2 ** (attempt - 1)
                    await asyncio.sleep(backoff)

        return NotificationResult(
            success=False,
            error=f"Failed after {self.retries} attempts",
            attempts=self.retries,
        )
