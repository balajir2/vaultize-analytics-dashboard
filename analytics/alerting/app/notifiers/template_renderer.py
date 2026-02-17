"""
Template Renderer

Handles {{alert.variable}} substitution in webhook bodies.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import re
from typing import Any, Dict

TEMPLATE_PATTERN = re.compile(r"\{\{alert\.([^}]+)\}\}")


class TemplateRenderer:
    """Renders template variables in webhook bodies."""

    def render(self, template: Any, context: Dict[str, Any]) -> Any:
        """Recursively substitute {{alert.xxx}} with context values."""
        if isinstance(template, str):
            return self._render_string(template, context)
        elif isinstance(template, dict):
            return {k: self.render(v, context) for k, v in template.items()}
        elif isinstance(template, list):
            return [self.render(item, context) for item in template]
        return template

    def _render_string(self, text: str, context: Dict[str, Any]) -> str:
        """Replace all {{alert.xxx}} patterns in a string."""
        def replacer(match):
            path = match.group(1)
            value = self._resolve_path(path, context)
            return str(value) if value is not None else match.group(0)
        return TEMPLATE_PATTERN.sub(replacer, text)

    def _resolve_path(self, path: str, context: Dict[str, Any]) -> Any:
        """Resolve dot-notation path against context dict."""
        current = context
        for part in path.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current
