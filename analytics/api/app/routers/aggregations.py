"""
Aggregations Router

API endpoints for log analytics and aggregations.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from opensearchpy import exceptions as os_exceptions

from app.models.common import APIResponse
from app.models.search import (
    AggregationRequest,
    AggregationResponse,
    AggregationBucket
)
from app.opensearch_client import get_opensearch

logger = logging.getLogger(__name__)

router = APIRouter()


def build_aggregation_query(agg_req: AggregationRequest) -> Dict[str, Any]:
    """
    Build OpenSearch aggregation query.

    Args:
        agg_req: Aggregation request parameters

    Returns:
        dict: OpenSearch aggregation query DSL
    """
    query_body = {
        "size": 0,  # Don't return documents, only aggregations
        "query": {"bool": {"must": [], "filter": []}},
        "aggs": {}
    }

    # Add filter query if provided
    if agg_req.query:
        query_body["query"]["bool"]["must"].append({
            "query_string": {
                "query": agg_req.query,
                "default_operator": "AND"
            }
        })
    else:
        query_body["query"]["bool"]["must"].append({"match_all": {}})

    # Add time range filter if provided
    if agg_req.time_range:
        time_filter = {"range": {}}
        time_filter["range"][agg_req.time_range.field] = {}

        if agg_req.time_range.start:
            time_filter["range"][agg_req.time_range.field]["gte"] = agg_req.time_range.start
        if agg_req.time_range.end:
            time_filter["range"][agg_req.time_range.field]["lte"] = agg_req.time_range.end

        query_body["query"]["bool"]["filter"].append(time_filter)

    # Build aggregation based on type
    if agg_req.agg_type == "terms":
        query_body["aggs"]["results"] = {
            "terms": {
                "field": agg_req.field,
                "size": agg_req.size or 10
            }
        }
    elif agg_req.agg_type == "date_histogram":
        if not agg_req.interval:
            raise ValueError("interval is required for date_histogram aggregation")

        query_body["aggs"]["results"] = {
            "date_histogram": {
                "field": agg_req.field,
                "fixed_interval": agg_req.interval
            }
        }
    elif agg_req.agg_type == "stats":
        query_body["aggs"]["results"] = {
            "stats": {
                "field": agg_req.field
            }
        }
    elif agg_req.agg_type == "cardinality":
        query_body["aggs"]["results"] = {
            "cardinality": {
                "field": agg_req.field
            }
        }
    else:
        raise ValueError(f"Unsupported aggregation type: {agg_req.agg_type}")

    return query_body


def parse_aggregation_response(response: Dict[str, Any], agg_type: str) -> list:
    """
    Parse OpenSearch aggregation response into buckets.

    Args:
        response: OpenSearch response
        agg_type: Aggregation type

    Returns:
        list: List of aggregation buckets
    """
    buckets = []

    if agg_type in ["terms", "date_histogram"]:
        # Bucket-based aggregations
        for bucket in response["aggregations"]["results"]["buckets"]:
            buckets.append(AggregationBucket(
                key=bucket["key"],
                doc_count=bucket["doc_count"],
                data=None
            ))
    elif agg_type == "stats":
        # Stats aggregation - single result
        stats = response["aggregations"]["results"]
        buckets.append(AggregationBucket(
            key="stats",
            doc_count=stats["count"],
            data={
                "min": stats.get("min"),
                "max": stats.get("max"),
                "avg": stats.get("avg"),
                "sum": stats.get("sum")
            }
        ))
    elif agg_type == "cardinality":
        # Cardinality - unique count
        value = response["aggregations"]["results"]["value"]
        buckets.append(AggregationBucket(
            key="unique_values",
            doc_count=value,
            data=None
        ))

    return buckets


@router.post("/aggregate", response_model=APIResponse[AggregationResponse])
async def aggregate_logs(agg_req: AggregationRequest):
    """
    Perform aggregations on log data.

    Execute analytics aggregations like top values, time histograms, statistics, etc.

    Supported aggregation types:
    - **terms**: Top N values for a field (e.g., top services, top error messages)
    - **date_histogram**: Time-based histogram (e.g., errors per hour)
    - **stats**: Statistical analysis (min, max, avg, sum)
    - **cardinality**: Unique value count

    Args:
        agg_req: Aggregation request parameters

    Returns:
        APIResponse[AggregationResponse]: Aggregation results

    Raises:
        HTTPException: If aggregation fails (400/500)

    Example:
        ```json
        {
            "query": "level:ERROR",
            "indices": ["logs-*"],
            "time_range": {
                "start": "now-24h",
                "end": "now"
            },
            "agg_type": "terms",
            "field": "service.keyword",
            "size": 10
        }
        ```
    """
    try:
        client = get_opensearch()
        query_body = build_aggregation_query(agg_req)

        logger.info(f"Executing {agg_req.agg_type} aggregation on {agg_req.field}")
        logger.debug(f"Query: {query_body}")

        # Execute aggregation
        response = client.search(
            index=",".join(agg_req.indices),
            body=query_body
        )

        # Parse response
        buckets = parse_aggregation_response(response, agg_req.agg_type)
        total = response["hits"]["total"]["value"]
        took = response["took"]

        agg_response = AggregationResponse(
            buckets=buckets,
            total=total,
            took=took
        )

        return APIResponse(
            status="success",
            data=agg_response,
            message=f"Aggregation completed in {took}ms"
        )

    except ValueError as e:
        logger.error(f"Invalid aggregation request: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except os_exceptions.RequestError as e:
        logger.error(f"Invalid aggregation query: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid query: {str(e)}"
        )
    except os_exceptions.NotFoundError as e:
        logger.error(f"Index not found: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Index not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Aggregation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Aggregation failed: {str(e)}"
        )


@router.get("/top-values/{field}", response_model=APIResponse[AggregationResponse])
async def get_top_values(
    field: str,
    indices: str = "logs-*",
    query: str = None,
    size: int = 10
):
    """
    Get top N values for a field (simplified terms aggregation).

    Quick endpoint to get the most common values for a field.

    Args:
        field: Field to aggregate (use .keyword for text fields)
        indices: Comma-separated index patterns
        query: Optional filter query
        size: Number of top values to return

    Returns:
        APIResponse[AggregationResponse]: Top values

    Example:
        GET /api/v1/top-values/level.keyword?size=5
    """
    agg_req = AggregationRequest(
        query=query,
        indices=indices.split(","),
        agg_type="terms",
        field=field,
        size=size
    )

    return await aggregate_logs(agg_req)
