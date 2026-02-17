"""
Alert Rule Models

Pydantic models matching the JSON alert rule format in configs/alert-rules/.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AlertSchedule(BaseModel):
    """Alert check schedule."""
    interval: str  # "5m", "1h", "30s"


class AlertQueryTimeRange(BaseModel):
    """Time range for alert query."""
    from_: str = Field(alias="from")  # "now-5m"
    to: str  # "now"

    model_config = {"populate_by_name": True}


class AlertQuery(BaseModel):
    """OpenSearch query definition for an alert."""
    index: List[str]
    time_field: str = "@timestamp"
    time_range: AlertQueryTimeRange
    filter: Dict[str, Any]
    aggregation: Optional[Dict[str, Any]] = None


class AlertCondition(BaseModel):
    """Threshold condition for firing an alert."""
    type: str = "threshold"
    operator: str  # gt, gte, lt, lte, eq
    value: float
    aggregation_field: Optional[str] = None  # e.g. "percentiles.95.0"


class WebhookConfig(BaseModel):
    """Webhook endpoint configuration."""
    url: str
    method: str = "POST"
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    body: Any = None


class AlertAction(BaseModel):
    """Alert notification action."""
    type: str = "webhook"
    name: str
    webhook: WebhookConfig


class AlertThrottle(BaseModel):
    """Throttle to prevent alert spam."""
    value: int
    unit: str  # "minutes", "hours", "seconds"


class AlertMetadata(BaseModel):
    """Alert metadata for categorization and ownership."""
    severity: str  # "critical", "high", "medium", "low"
    category: str
    owner: str
    runbook: Optional[str] = None
    created_by: Optional[str] = None
    created_date: Optional[str] = None
    tags: List[str] = []


class AlertRule(BaseModel):
    """
    Complete alert rule definition.

    Matches the JSON format in configs/alert-rules/*.json.
    """
    name: str
    description: str
    enabled: bool = True
    schedule: AlertSchedule
    query: AlertQuery
    condition: AlertCondition
    actions: List[AlertAction]
    throttle: AlertThrottle
    metadata: AlertMetadata
    file_path: Optional[str] = None
