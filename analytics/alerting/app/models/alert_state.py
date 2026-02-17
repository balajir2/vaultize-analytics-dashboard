"""
Alert State Models

Models for tracking alert state transitions.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AlertState(str, Enum):
    """Possible states for an alert rule."""
    OK = "ok"
    FIRING = "firing"
    RESOLVED = "resolved"


@dataclass
class AlertStateRecord:
    """Persisted state record for a single alert rule."""
    rule_name: str
    state: AlertState = AlertState.OK
    last_checked: Optional[datetime] = None
    last_fired: Optional[datetime] = None
    last_resolved: Optional[datetime] = None
    last_notified: Optional[datetime] = None
    consecutive_fires: int = 0
    current_value: Optional[float] = None
    threshold: float = 0.0
    message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "rule_name": self.rule_name,
            "state": self.state.value,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "last_fired": self.last_fired.isoformat() if self.last_fired else None,
            "last_resolved": self.last_resolved.isoformat() if self.last_resolved else None,
            "last_notified": self.last_notified.isoformat() if self.last_notified else None,
            "consecutive_fires": self.consecutive_fires,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AlertStateRecord":
        def parse_dt(val):
            if val is None:
                return None
            if isinstance(val, datetime):
                return val
            return datetime.fromisoformat(val)

        return cls(
            rule_name=data["rule_name"],
            state=AlertState(data.get("state", "ok")),
            last_checked=parse_dt(data.get("last_checked")),
            last_fired=parse_dt(data.get("last_fired")),
            last_resolved=parse_dt(data.get("last_resolved")),
            last_notified=parse_dt(data.get("last_notified")),
            consecutive_fires=data.get("consecutive_fires", 0),
            current_value=data.get("current_value"),
            threshold=data.get("threshold", 0.0),
            message=data.get("message"),
        )


@dataclass
class StateTransition:
    """Result of evaluating a state transition."""
    previous_state: AlertState
    new_state: AlertState
    changed: bool
    should_notify: bool
