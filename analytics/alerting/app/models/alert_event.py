"""
Alert Event Models

Models for alert history events stored in .alerts-history.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AlertEvent:
    """A single alert event for history tracking."""
    rule_name: str
    event_type: str  # "fired", "resolved", "error"
    timestamp: datetime
    value: Optional[float] = None
    threshold: float = 0.0
    operator: str = ""
    condition_met: bool = False
    notification_sent: bool = False
    notification_status: Optional[str] = None  # "success", "partial", "failed"
    notification_results: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    query_took_ms: Optional[int] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "rule_name": self.rule_name,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "threshold": self.threshold,
            "operator": self.operator,
            "condition_met": self.condition_met,
            "notification_sent": self.notification_sent,
            "notification_status": self.notification_status,
            "notification_results": self.notification_results,
            "metadata": self.metadata,
            "query_took_ms": self.query_took_ms,
            "error": self.error,
        }
