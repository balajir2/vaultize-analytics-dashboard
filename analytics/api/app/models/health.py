"""
Health Check Models

Pydantic models for health check endpoints.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from typing import Optional
from pydantic import BaseModel, Field


class OpenSearchHealthResponse(BaseModel):
    """
    OpenSearch cluster health information.
    """
    cluster_name: str = Field(..., description="Name of the OpenSearch cluster")
    status: str = Field(..., description="Cluster status: green, yellow, or red")
    timed_out: bool = Field(..., description="Whether the health check timed out")
    number_of_nodes: int = Field(..., description="Total number of nodes in cluster")
    number_of_data_nodes: int = Field(..., description="Number of data nodes")
    active_primary_shards: int = Field(..., description="Number of active primary shards")
    active_shards: int = Field(..., description="Total number of active shards")
    relocating_shards: int = Field(..., description="Number of shards being relocated")
    initializing_shards: int = Field(..., description="Number of shards being initialized")
    unassigned_shards: int = Field(..., description="Number of unassigned shards")

    class Config:
        json_schema_extra = {
            "example": {
                "cluster_name": "vaultize-opensearch-cluster",
                "status": "green",
                "timed_out": False,
                "number_of_nodes": 3,
                "number_of_data_nodes": 3,
                "active_primary_shards": 15,
                "active_shards": 30,
                "relocating_shards": 0,
                "initializing_shards": 0,
                "unassigned_shards": 0
            }
        }


class HealthResponse(BaseModel):
    """
    Overall API health status.
    """
    status: str = Field(..., description="API health status: healthy or unhealthy")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Deployment environment")
    opensearch: Optional[OpenSearchHealthResponse] = Field(
        default=None,
        description="OpenSearch cluster health (if available)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "environment": "development",
                "opensearch": {
                    "cluster_name": "vaultize-opensearch-cluster",
                    "status": "green",
                    "timed_out": False,
                    "number_of_nodes": 3,
                    "number_of_data_nodes": 3,
                    "active_primary_shards": 15,
                    "active_shards": 30,
                    "relocating_shards": 0,
                    "initializing_shards": 0,
                    "unassigned_shards": 0
                }
            }
        }
