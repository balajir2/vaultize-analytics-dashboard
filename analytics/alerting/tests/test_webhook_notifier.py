"""
Tests for webhook.py (WebhookNotifier)

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest
import httpx
import respx

from app.models.alert_rule import AlertAction, WebhookConfig
from app.notifiers.webhook import NotificationContext, NotificationResult, WebhookNotifier


@pytest.fixture
def notifier():
    return WebhookNotifier(timeout=5, retries=3)


@pytest.fixture
def sample_action():
    return AlertAction(
        type="webhook",
        name="test_hook",
        webhook=WebhookConfig(
            url="http://hooks.example.com/test",
            method="POST",
            headers={"Content-Type": "application/json"},
            body={"text": "Alert: {{alert.name}}", "count": "{{alert.result_count}}"},
        ),
    )


@pytest.fixture
def sample_context():
    return NotificationContext(
        name="High Error Rate",
        description="Error count alert",
        result_count=150.0,
        threshold=100.0,
        timestamp="2026-02-10T12:00:00Z",
        severity="high",
        environment="production",
        service="api-gateway",
        state="firing",
        operator="gt",
    )


class TestWebhookNotifier:
    """Tests for the WebhookNotifier class."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_successful_send(self, notifier, sample_action, sample_context):
        route = respx.post("http://hooks.example.com/test").respond(200, json={"ok": True})
        result = await notifier.send(sample_action, sample_context)

        assert result.success is True
        assert result.status_code == 200
        assert result.attempts == 1
        assert route.called

    @respx.mock
    @pytest.mark.asyncio
    async def test_retry_on_server_error(self, notifier, sample_action, sample_context):
        route = respx.post("http://hooks.example.com/test").mock(
            side_effect=[
                httpx.Response(500, json={"error": "server error"}),
                httpx.Response(500, json={"error": "server error"}),
                httpx.Response(200, json={"ok": True}),
            ]
        )
        result = await notifier.send(sample_action, sample_context)

        assert result.success is True
        assert result.attempts == 3

    @respx.mock
    @pytest.mark.asyncio
    async def test_all_retries_exhausted(self, notifier, sample_action, sample_context):
        respx.post("http://hooks.example.com/test").respond(500, json={"error": "down"})
        result = await notifier.send(sample_action, sample_context)

        assert result.success is False
        assert result.attempts == 3
        assert "Failed after 3 attempts" in result.error

    @respx.mock
    @pytest.mark.asyncio
    async def test_connection_error_retries(self, notifier, sample_action, sample_context):
        respx.post("http://hooks.example.com/test").mock(
            side_effect=httpx.ConnectError("connection refused")
        )
        result = await notifier.send(sample_action, sample_context)

        assert result.success is False
        assert result.attempts == 3

    @respx.mock
    @pytest.mark.asyncio
    async def test_template_rendering_in_body(self, notifier, sample_action, sample_context):
        route = respx.post("http://hooks.example.com/test").respond(200)
        await notifier.send(sample_action, sample_context)

        request = route.calls.last.request
        body = request.content
        # The body should have been rendered with actual values
        assert b"High Error Rate" in body
        assert b"150" in body

    @respx.mock
    @pytest.mark.asyncio
    async def test_status_201_is_success(self, notifier, sample_action, sample_context):
        respx.post("http://hooks.example.com/test").respond(201)
        result = await notifier.send(sample_action, sample_context)
        assert result.success is True
        assert result.status_code == 201

    @pytest.mark.asyncio
    async def test_notification_context_to_dict(self, sample_context):
        d = sample_context.to_dict()
        assert d["name"] == "High Error Rate"
        assert d["severity"] == "high"
        # None values excluded
        assert "p95_response_time" not in d

    @pytest.mark.asyncio
    async def test_single_retry_notifier(self, sample_action, sample_context):
        """Notifier with retries=1 should only try once."""
        single_notifier = WebhookNotifier(timeout=5, retries=1)
        with respx.mock:
            respx.post("http://hooks.example.com/test").respond(500)
            result = await single_notifier.send(sample_action, sample_context)
            assert result.success is False
            assert result.attempts == 1
