"""
OpenSearch Client Module

Manages connection and operations with OpenSearch cluster.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from typing import Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from app.config import settings

logger = logging.getLogger(__name__)


class OpenSearchClient:
    """Singleton OpenSearch client for the alerting service."""

    _instance: Optional[OpenSearch] = None

    @classmethod
    def get_client(cls) -> OpenSearch:
        if cls._instance is None:
            cls._instance = cls._create_client()
        return cls._instance

    @classmethod
    def _create_client(cls) -> OpenSearch:
        logger.info(f"Connecting to OpenSearch at {settings.opensearch_url}")
        client = OpenSearch(
            hosts=[{"host": settings.opensearch_host, "port": settings.opensearch_port}],
            http_auth=(settings.opensearch_user, settings.opensearch_password),
            use_ssl=settings.opensearch_scheme == "https",
            verify_certs=settings.opensearch_verify_certs,
            ssl_show_warn=False,
            connection_class=RequestsHttpConnection,
            timeout=settings.opensearch_timeout,
        )
        try:
            info = client.info()
            logger.info(f"Connected to OpenSearch {info['version']['number']}")
        except Exception as e:
            logger.error(f"Failed to connect to OpenSearch: {e}")
            raise ConnectionError(f"Cannot connect to OpenSearch: {e}")
        return client

    @classmethod
    def health_check(cls) -> dict:
        return cls.get_client().cluster.health()

    @classmethod
    def close(cls):
        if cls._instance:
            cls._instance.close()
            cls._instance = None
            logger.info("OpenSearch client closed")


def get_opensearch() -> OpenSearch:
    """Dependency injection helper for FastAPI routes."""
    return OpenSearchClient.get_client()
