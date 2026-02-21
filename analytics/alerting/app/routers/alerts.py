"""
Alerts Management Router

Endpoints for listing rules, checking status, manual triggers, and history.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query

from app.middleware.auth import require_admin

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_scheduler(request: Request):
    """Extract scheduler from app state."""
    scheduler = getattr(request.app.state, "scheduler", None)
    if scheduler is None:
        raise HTTPException(status_code=503, detail="Alerting service not initialized")
    return scheduler


@router.get("/rules")
async def list_rules(request: Request):
    """List all loaded alert rules with their current state."""
    scheduler = _get_scheduler(request)
    rules = scheduler.rule_loader.rules
    result = []
    for name, rule in rules.items():
        state = scheduler.state_manager.get_state(name)
        result.append({
            "name": name,
            "description": rule.description,
            "enabled": rule.enabled,
            "schedule": rule.schedule.interval,
            "severity": rule.metadata.severity,
            "state": state.state.value,
            "last_checked": state.last_checked.isoformat() if state.last_checked else None,
        })
    return {"status": "success", "data": result}


@router.get("/rules/{rule_name}/status")
async def get_rule_status(request: Request, rule_name: str):
    """Get detailed status of a specific rule."""
    scheduler = _get_scheduler(request)
    rule = scheduler.rule_loader.get_rule(rule_name)
    if rule is None:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_name}' not found")

    state = scheduler.state_manager.get_state(rule_name)
    return {
        "status": "success",
        "data": {
            "rule": {
                "name": rule.name,
                "description": rule.description,
                "enabled": rule.enabled,
                "schedule": rule.schedule.interval,
                "condition": {
                    "operator": rule.condition.operator,
                    "value": rule.condition.value,
                },
                "severity": rule.metadata.severity,
            },
            "state": state.to_dict(),
        },
    }


@router.post("/rules/{rule_name}/trigger", dependencies=[Depends(require_admin)])
async def trigger_rule(request: Request, rule_name: str):
    """Manually trigger an alert check."""
    scheduler = _get_scheduler(request)
    event = await scheduler.trigger_manual(rule_name)
    if event is None:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_name}' not found")
    return {"status": "success", "data": event.to_dict()}


@router.get("/history")
async def get_history(
    request: Request,
    rule_name: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    time_from: str = Query("now-24h"),
):
    """Query alert history."""
    scheduler = _get_scheduler(request)
    events = scheduler.history_storage.get_history(
        rule_name=rule_name, limit=limit, time_from=time_from
    )
    return {"status": "success", "data": events}


@router.post("/rules/reload", dependencies=[Depends(require_admin)])
async def reload_rules(request: Request):
    """Force reload of alert rule files."""
    scheduler = _get_scheduler(request)
    scheduler.reload_rules()
    count = len(scheduler.rule_loader.get_enabled_rules())
    return {"status": "success", "message": f"Reloaded {count} enabled rules"}
