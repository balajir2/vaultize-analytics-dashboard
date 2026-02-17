"""
Rule Loader Service

Loads and validates alert rules from JSON config files.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

from app.models.alert_rule import AlertRule

logger = logging.getLogger(__name__)

ENV_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")


class RuleLoader:
    """Loads alert rules from JSON files in a configured directory."""

    def __init__(self, rules_dir: str):
        self.rules_dir = Path(rules_dir)
        self._rules: Dict[str, AlertRule] = {}

    def load_all_rules(self) -> Dict[str, AlertRule]:
        """Load all .json rule files from the rules directory."""
        self._rules.clear()

        if not self.rules_dir.exists():
            logger.warning(f"Alert rules directory not found: {self.rules_dir}")
            return self._rules

        for file_path in sorted(self.rules_dir.glob("*.json")):
            if file_path.name == "README.md":
                continue
            try:
                rule = self.load_rule(file_path)
                self._rules[rule.name] = rule
                logger.info(f"Loaded alert rule: {rule.name} (enabled={rule.enabled})")
            except Exception as e:
                logger.error(f"Failed to load rule from {file_path}: {e}")

        logger.info(f"Loaded {len(self._rules)} alert rules")
        return self._rules

    def load_rule(self, file_path: Path) -> AlertRule:
        """Load and validate a single rule file."""
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        resolved_data = self._resolve_env_vars(raw_data)
        rule = AlertRule.model_validate(resolved_data)
        rule.file_path = str(file_path)
        return rule

    def reload_rules(self) -> Dict[str, AlertRule]:
        """Reload all rules from disk."""
        logger.info("Reloading alert rules")
        return self.load_all_rules()

    def get_enabled_rules(self) -> List[AlertRule]:
        """Return only enabled rules."""
        return [r for r in self._rules.values() if r.enabled]

    def get_rule(self, name: str) -> Optional[AlertRule]:
        """Get a specific rule by name."""
        return self._rules.get(name)

    @property
    def rules(self) -> Dict[str, AlertRule]:
        return self._rules

    def _resolve_env_vars(self, value: Any) -> Any:
        """Recursively replace ${ENV_VAR} patterns with environment variable values."""
        if isinstance(value, str):
            return ENV_VAR_PATTERN.sub(
                lambda m: os.environ.get(m.group(1), m.group(0)),
                value,
            )
        elif isinstance(value, dict):
            return {k: self._resolve_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._resolve_env_vars(item) for item in value]
        return value
