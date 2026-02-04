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
    """
    Singleton OpenSearch client for the application.

    Manages connection pooling and provides helper methods for common operations.
    """

    _instance: Optional[OpenSearch] = None

    @classmethod
    def get_client(cls) -> OpenSearch:
        """
        Get or create OpenSearch client instance.

        Returns:
            OpenSearch: Connected client instance

        Raises:
            ConnectionError: If unable to connect to OpenSearch
        """
        if cls._instance is None:
            cls._instance = cls._create_client()
        return cls._instance

    @classmethod
    def _create_client(cls) -> OpenSearch:
        """
        Create new OpenSearch client with connection pooling.

        Returns:
            OpenSearch: New client instance
        """
        logger.info(f"Connecting to OpenSearch at {settings.opensearch_url}")

        client = OpenSearch(
            hosts=[{
                "host": settings.opensearch_host,
                "port": settings.opensearch_port
            }],
            http_auth=(settings.opensearch_user, settings.opensearch_password),
            use_ssl=settings.opensearch_scheme == "https",
            verify_certs=settings.opensearch_verify_certs,
            ssl_show_warn=False,
            connection_class=RequestsHttpConnection,
            pool_maxsize=settings.opensearch_max_connections,
            timeout=settings.opensearch_timeout,
        )

        # Test connection
        try:
            info = client.info()
            logger.info(f"Connected to OpenSearch {info['version']['number']}")
        except Exception as e:
            logger.error(f"Failed to connect to OpenSearch: {e}")
            raise ConnectionError(f"Cannot connect to OpenSearch: {e}")

        return client

    @classmethod
    def health_check(cls) -> dict:
        """
        Check OpenSearch cluster health.

        Returns:
            dict: Cluster health information
        """
        client = cls.get_client()
        return client.cluster.health()

    @classmethod
    def close(cls):
        """Close the OpenSearch client connection."""
        if cls._instance:
            cls._instance.close()
            cls._instance = None
            logger.info("OpenSearch client closed")


# ============================================================================
# Helper Functions
# ============================================================================

def get_opensearch() -> OpenSearch:
    """
    Dependency injection helper for FastAPI routes.

    Returns:
        OpenSearch: Client instance
    """
    return OpenSearchClient.get_client()
