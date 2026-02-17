"""
Tests for template_renderer.py

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from app.notifiers.template_renderer import TemplateRenderer


class TestTemplateRenderer:
    """Tests for the TemplateRenderer class."""

    def setup_method(self):
        self.renderer = TemplateRenderer()
        self.context = {
            "name": "High Error Rate",
            "result_count": 150,
            "threshold": 100,
            "timestamp": "2026-02-10T12:00:00Z",
            "severity": "high",
            "environment": "production",
            "service": "api-gateway",
        }

    def test_simple_string_substitution(self):
        template = "Alert: {{alert.name}}"
        result = self.renderer.render(template, self.context)
        assert result == "Alert: High Error Rate"

    def test_multiple_substitutions_in_string(self):
        template = "{{alert.name}}: count={{alert.result_count}}, threshold={{alert.threshold}}"
        result = self.renderer.render(template, self.context)
        assert result == "High Error Rate: count=150, threshold=100"

    def test_dict_template(self):
        template = {
            "text": "Alert: {{alert.name}}",
            "value": "{{alert.result_count}}",
        }
        result = self.renderer.render(template, self.context)
        assert result["text"] == "Alert: High Error Rate"
        assert result["value"] == "150"

    def test_list_template(self):
        template = ["{{alert.name}}", "{{alert.severity}}"]
        result = self.renderer.render(template, self.context)
        assert result == ["High Error Rate", "high"]

    def test_nested_dict_template(self):
        template = {
            "blocks": [
                {"text": "{{alert.name}}"},
                {"fields": [{"value": "{{alert.severity}}"}]},
            ]
        }
        result = self.renderer.render(template, self.context)
        assert result["blocks"][0]["text"] == "High Error Rate"
        assert result["blocks"][1]["fields"][0]["value"] == "high"

    def test_missing_variable_preserved(self):
        template = "Alert: {{alert.nonexistent}}"
        result = self.renderer.render(template, self.context)
        assert result == "Alert: {{alert.nonexistent}}"

    def test_non_string_passthrough(self):
        assert self.renderer.render(42, self.context) == 42
        assert self.renderer.render(True, self.context) is True
        assert self.renderer.render(None, self.context) is None

    def test_numeric_value_converted_to_string(self):
        template = "Count: {{alert.result_count}}"
        result = self.renderer.render(template, self.context)
        assert result == "Count: 150"

    def test_nested_context_access(self):
        context = {"meta": {"severity": "critical"}}
        template = "Severity: {{alert.meta.severity}}"
        result = self.renderer.render(template, context)
        assert result == "Severity: critical"

    def test_empty_string_template(self):
        result = self.renderer.render("", self.context)
        assert result == ""

    def test_no_template_markers(self):
        result = self.renderer.render("plain text", self.context)
        assert result == "plain text"
