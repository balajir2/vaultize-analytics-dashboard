"""
OpenSearch Storage

Persists alert events to the .alerts-history index.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from typing import List, Optional

from opensearchpy import OpenSearch

from app.models.alert_event import AlertEvent

logger = logging.getLogger(__name__)


class AlertHistoryStorage:
    """Stores and queries alert history events in OpenSearch."""

    def __init__(self, client: OpenSearch, history_index: str):
        self.client = client
        self.history_index = history_index

    def initialize(self):
        """Create history index with mappings if it doesn't exist."""
        if not self.client.indices.exists(index=self.history_index):
            self.client.indices.create(
                index=self.history_index,
                body={
                    "settings": {"number_of_shards": 1, "number_of_replicas": 1},
                    "mappings": {
                        "properties": {
                            "rule_name": {"type": "keyword"},
                            "event_type": {"type": "keyword"},
                            "timestamp": {"type": "date"},
                            "value": {"type": "float"},
                            "threshold": {"type": "float"},
                            "operator": {"type": "keyword"},
                            "condition_met": {"type": "boolean"},
                            "notification_sent": {"type": "boolean"},
                            "notification_status": {"type": "keyword"},
                            "metadata": {"type": "object", "enabled": True},
                            "query_took_ms": {"type": "integer"},
                            "error": {"type": "text"},
                        }
                    },
                },
            )
            logger.info(f"Created index: {self.history_index}")

    def record_event(self, event: AlertEvent):
        """Index an alert event into history."""
        try:
            self.client.index(
                index=self.history_index,
                body=event.to_dict(),
            )
        except Exception as e:
            logger.error(f"Failed to record alert event: {e}")

    def get_history(
        self,
        rule_name: Optional[str] = None,
        limit: int = 100,
        time_from: str = "now-24h",
    ) -> List[dict]:
        """Query alert history, optionally filtered by rule name."""
        must_clauses = [{"range": {"timestamp": {"gte": time_from}}}]
        if rule_name:
            must_clauses.append({"term": {"rule_name": rule_name}})

        try:
            response = self.client.search(
                index=self.history_index,
                body={
                    "query": {"bool": {"must": must_clauses}},
                    "sort": [{"timestamp": {"order": "desc"}}],
                    "size": limit,
                },
            )
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            logger.error(f"Failed to query alert history: {e}")
            return []
