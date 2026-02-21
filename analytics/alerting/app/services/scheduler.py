"""
Alert Scheduler

Orchestrates periodic alert checks using APScheduler.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
import re
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.models.alert_event import AlertEvent
from app.models.alert_rule import AlertRule
from app.models.alert_state import AlertState
from app.notifiers.webhook import NotificationContext, WebhookNotifier
from app.services.condition_evaluator import ConditionEvaluator
from app.services.query_executor import QueryExecutor
from app.services.rule_loader import RuleLoader
from app.services.state_manager import StateManager
from app.storage.opensearch_storage import AlertHistoryStorage

logger = logging.getLogger(__name__)

INTERVAL_PATTERN = re.compile(r"^(\d+)([smhd])$")
INTERVAL_UNITS = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days"}


class AlertScheduler:
    """Ties all alerting services together with periodic scheduling."""

    def __init__(
        self,
        rule_loader: RuleLoader,
        query_executor: QueryExecutor,
        condition_evaluator: ConditionEvaluator,
        state_manager: StateManager,
        notifier: WebhookNotifier,
        history_storage: AlertHistoryStorage,
    ):
        self.rule_loader = rule_loader
        self.query_executor = query_executor
        self.condition_evaluator = condition_evaluator
        self.state_manager = state_manager
        self.notifier = notifier
        self.history_storage = history_storage
        self.scheduler = AsyncIOScheduler()
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self):
        """Load rules, schedule jobs, and start the scheduler."""
        self.rule_loader.load_all_rules()
        rules = self.rule_loader.get_enabled_rules()

        for rule in rules:
            self._schedule_rule(rule)

        self.scheduler.start()
        self._running = True
        logger.info(f"Scheduler started with {len(rules)} alert rules")

    def stop(self):
        """Gracefully stop the scheduler."""
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("Scheduler stopped")

    def reload_rules(self):
        """Reload rules from disk and reschedule."""
        self.scheduler.remove_all_jobs()
        self.rule_loader.reload_rules()
        rules = self.rule_loader.get_enabled_rules()

        for rule in rules:
            self._schedule_rule(rule)

        logger.info(f"Reloaded and rescheduled {len(rules)} alert rules")

    def _schedule_rule(self, rule: AlertRule):
        """Schedule a periodic check for a single rule."""
        interval_kwargs = self._parse_interval(rule.schedule.interval)
        self.scheduler.add_job(
            self._check_alert,
            trigger=IntervalTrigger(**interval_kwargs),
            args=[rule],
            id=f"alert_{rule.name}",
            name=f"Alert: {rule.name}",
            replace_existing=True,
        )
        logger.debug(f"Scheduled rule '{rule.name}' every {rule.schedule.interval}")

    async def _check_alert(self, rule: AlertRule):
        """
        Main alert check loop for one rule:
        1. Execute query
        2. Evaluate condition
        3. Update state
        4. Send notification if needed
        5. Record history event
        """
        now = datetime.now(timezone.utc)
        logger.debug(f"Checking alert: {rule.name}")

        # 1. Execute query
        query_result = self.query_executor.execute(rule)
        if not query_result.success:
            self.history_storage.record_event(AlertEvent(
                rule_name=rule.name,
                event_type="error",
                timestamp=now,
                threshold=rule.condition.value,
                operator=rule.condition.operator,
                error=query_result.error,
            ))
            return

        # 2. Evaluate condition
        eval_result = self.condition_evaluator.evaluate(rule, query_result)
        logger.debug(eval_result.message)

        # 3. Update state
        transition = self.state_manager.update_state(
            rule, eval_result.condition_met, eval_result.actual_value
        )

        # 4. Send notification if needed
        notification_sent = False
        notification_status = None
        notification_results = []

        if transition.should_notify:
            event_type = "fired" if transition.new_state == AlertState.FIRING else "resolved"
            context = NotificationContext(
                name=rule.name,
                description=rule.description,
                result_count=eval_result.actual_value,
                threshold=eval_result.threshold,
                timestamp=now.isoformat(),
                severity=rule.metadata.severity,
                environment=rule.metadata.category,
                service=rule.metadata.owner,
                state=transition.new_state.value,
                operator=eval_result.operator,
            )
            for action in rule.actions:
                result = await self.notifier.send(action, context)
                notification_results.append({
                    "action": action.type if hasattr(action, "type") else str(action),
                    "success": result.success,
                    "status": "success" if result.success else "failed",
                })

            # Compute aggregate status from all results
            if notification_results:
                successes = sum(1 for r in notification_results if r["success"])
                total = len(notification_results)
                notification_sent = successes > 0
                if successes == total:
                    notification_status = "success"
                elif successes > 0:
                    notification_status = "partial"
                else:
                    notification_status = "failed"

        # 5. Record history event
        if transition.changed or transition.should_notify:
            event_type = "fired" if transition.new_state == AlertState.FIRING else "resolved"
            self.history_storage.record_event(AlertEvent(
                rule_name=rule.name,
                event_type=event_type,
                timestamp=now,
                value=eval_result.actual_value,
                threshold=eval_result.threshold,
                operator=eval_result.operator,
                condition_met=eval_result.condition_met,
                notification_sent=notification_sent,
                notification_status=notification_status,
                notification_results=notification_results,
                metadata={"severity": rule.metadata.severity, "category": rule.metadata.category},
                query_took_ms=query_result.took_ms,
            ))

    async def trigger_manual(self, rule_name: str) -> Optional[AlertEvent]:
        """Manually trigger an alert check for a specific rule."""
        rule = self.rule_loader.get_rule(rule_name)
        if rule is None:
            return None

        await self._check_alert(rule)
        state = self.state_manager.get_state(rule_name)
        return AlertEvent(
            rule_name=rule_name,
            event_type="manual_trigger",
            timestamp=datetime.now(timezone.utc),
            value=state.current_value,
            threshold=state.threshold,
            condition_met=state.state == AlertState.FIRING,
        )

    @staticmethod
    def _parse_interval(interval_str: str) -> dict:
        """Parse interval string like '5m' into kwargs for IntervalTrigger."""
        match = INTERVAL_PATTERN.match(interval_str)
        if not match:
            raise ValueError(f"Invalid interval format: {interval_str}")
        value = int(match.group(1))
        unit_key = match.group(2)
        unit_name = INTERVAL_UNITS[unit_key]
        return {unit_name: value}
