"""
State Manager Service

Tracks alert states, enforces throttling, manages state transitions.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from opensearchpy import OpenSearch

from app.models.alert_rule import AlertRule, AlertThrottle
from app.models.alert_state import AlertState, AlertStateRecord, StateTransition

logger = logging.getLogger(__name__)


class StateManager:
    """Manages alert state transitions and throttle enforcement."""

    def __init__(self, client: OpenSearch, state_index: str):
        self.client = client
        self.state_index = state_index
        self._states: Dict[str, AlertStateRecord] = {}

    def initialize(self):
        """Create state index if needed and load existing states."""
        if not self.client.indices.exists(index=self.state_index):
            self.client.indices.create(
                index=self.state_index,
                body={
                    "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                    "mappings": {
                        "properties": {
                            "rule_name": {"type": "keyword"},
                            "state": {"type": "keyword"},
                            "last_checked": {"type": "date"},
                            "last_fired": {"type": "date"},
                            "last_resolved": {"type": "date"},
                            "last_notified": {"type": "date"},
                            "consecutive_fires": {"type": "integer"},
                            "current_value": {"type": "float"},
                            "threshold": {"type": "float"},
                            "message": {"type": "text"},
                        }
                    },
                },
            )
            logger.info(f"Created index: {self.state_index}")
        self._load_states()

    def get_state(self, rule_name: str) -> AlertStateRecord:
        """Get current state for a rule, defaults to OK."""
        if rule_name not in self._states:
            self._states[rule_name] = AlertStateRecord(rule_name=rule_name)
        return self._states[rule_name]

    def update_state(
        self, rule: AlertRule, condition_met: bool, current_value: float
    ) -> StateTransition:
        """Evaluate and apply state transition."""
        state_record = self.get_state(rule.name)
        now = datetime.now(timezone.utc)
        previous_state = state_record.state

        state_record.last_checked = now
        state_record.current_value = current_value
        state_record.threshold = rule.condition.value

        if condition_met:
            if previous_state in (AlertState.OK, AlertState.RESOLVED):
                # Transition to FIRING
                state_record.state = AlertState.FIRING
                state_record.last_fired = now
                state_record.consecutive_fires = 1
                should_notify = True
            else:
                # Already FIRING, increment counter
                state_record.consecutive_fires += 1
                should_notify = self.should_notify(rule, rule.name)
        else:
            if previous_state == AlertState.FIRING:
                # Transition to RESOLVED
                state_record.state = AlertState.RESOLVED
                state_record.last_resolved = now
                state_record.consecutive_fires = 0
                should_notify = True
            elif previous_state == AlertState.RESOLVED:
                # Back to OK
                state_record.state = AlertState.OK
                state_record.consecutive_fires = 0
                should_notify = False
            else:
                # Stay OK
                should_notify = False

        new_state = state_record.state
        changed = previous_state != new_state

        if should_notify:
            state_record.last_notified = now

        self._persist_state(rule.name, state_record)

        return StateTransition(
            previous_state=previous_state,
            new_state=new_state,
            changed=changed,
            should_notify=should_notify,
        )

    def should_notify(self, rule: AlertRule, rule_name: str) -> bool:
        """Check if notification is allowed (throttle window passed)."""
        state_record = self.get_state(rule_name)
        if state_record.last_notified is None:
            return True

        throttle_seconds = self._parse_throttle_seconds(rule.throttle)
        now = datetime.now(timezone.utc)
        elapsed = (now - state_record.last_notified).total_seconds()
        return elapsed >= throttle_seconds

    def _persist_state(self, rule_name: str, state: AlertStateRecord):
        """Write state to OpenSearch."""
        try:
            self.client.index(
                index=self.state_index,
                id=rule_name,
                body=state.to_dict(),
                refresh="wait_for",
            )
        except Exception as e:
            logger.error(f"Failed to persist state for '{rule_name}': {e}")

    def _load_states(self):
        """Load existing states from OpenSearch."""
        try:
            response = self.client.search(
                index=self.state_index,
                body={"query": {"match_all": {}}, "size": 1000},
            )
            for hit in response["hits"]["hits"]:
                record = AlertStateRecord.from_dict(hit["_source"])
                self._states[record.rule_name] = record
            logger.info(f"Loaded {len(self._states)} existing alert states")
        except Exception as e:
            logger.warning(f"Could not load existing states: {e}")

    @staticmethod
    def _parse_throttle_seconds(throttle: AlertThrottle) -> int:
        """Convert throttle config to seconds."""
        multipliers = {"seconds": 1, "minutes": 60, "hours": 3600}
        return throttle.value * multipliers.get(throttle.unit, 60)
