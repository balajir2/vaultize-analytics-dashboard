"""
Regression Test RT-006: Sample Data Generator Windows Encoding Compatibility

Original Bug:
    The sample log generator used Unicode symbols (checkmarks, crosses) in
    output messages (e.g., "✓ Success", "✗ Failed"). On Windows systems
    with default cp1252 encoding, this caused UnicodeEncodeError crashes
    when printing to console.

How to Reproduce:
    1. Run generate_sample_logs.py on Windows with default console encoding
    2. Script crashes with UnicodeEncodeError on first Unicode symbol output

Fix Applied:
    - Replaced Unicode symbols with ASCII equivalents: [OK], [ERROR]
    - Ensured all output strings use only ASCII-safe characters
    - JSON data itself uses UTF-8 (handled by json.dumps)

Date: 2026-02-06
Severity: Medium
"""

import pytest
import ast
from pathlib import Path


class TestRegressionSampleDataEncoding:
    """Regression tests for sample data generator encoding issues"""

    @pytest.fixture
    def generator_path(self):
        """Path to sample log generator"""
        return Path("scripts/data/generate_sample_logs.py")

    @pytest.fixture
    def generator_source(self, generator_path):
        """Read generator source code"""
        with open(generator_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_regression_006_no_unicode_symbols_in_output(self, generator_source):
        """
        Verify that the generator does not use Unicode symbols in print
        statements that would fail on Windows cp1252 encoding.
        """
        problematic_chars = ['✓', '✗', '✅', '❌', '⚠', '🔍', '📊', '🚨']

        for char in problematic_chars:
            assert char not in generator_source, (
                f"Unicode symbol '{char}' found in generator source. "
                f"Use ASCII alternatives like [OK], [ERROR] for Windows compatibility."
            )

    def test_regression_006_uses_ascii_status_indicators(self, generator_source):
        """
        Verify that status output uses ASCII-safe indicators.
        """
        # The generator should use [OK] and [ERROR] patterns
        assert '[OK]' in generator_source or 'OK' in generator_source, (
            "Generator should use ASCII-safe status indicators like [OK]"
        )

    def test_regression_006_generator_is_valid_python(self, generator_path):
        """
        Verify that the generator script is valid Python that can be parsed.
        """
        with open(generator_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Should parse without errors
        tree = ast.parse(source)
        assert tree is not None, "Generator script failed to parse"

    def test_regression_006_log_entries_are_json_serializable(self):
        """
        Verify that generated log entries can be serialized to JSON
        without encoding issues. Uses the real generator function.
        """
        import json
        import sys
        from datetime import datetime, timezone

        # Import the real generator module
        scripts_dir = str(Path("scripts/data").resolve())
        sys.path.insert(0, scripts_dir)
        from generate_sample_logs import generate_log_entry

        # Generate a real log entry using the actual generator
        log_entry = generate_log_entry(datetime.now(timezone.utc))

        # Must serialize without errors
        json_str = json.dumps(log_entry)
        assert json_str is not None

        # Must round-trip through JSON without data loss
        decoded = json.loads(json_str)
        assert decoded["level"] in ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
        assert "@timestamp" in decoded
        assert "service" in decoded
