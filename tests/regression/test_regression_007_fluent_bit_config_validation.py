"""
Regression Test RT-007: Fluent Bit Configuration Validation

Original Issue:
    Fluent Bit configuration must follow strict INI-style format with
    required sections and valid directives. Misconfigured Fluent Bit
    causes silent log loss - events are dropped without errors.

Key Requirements:
    - Must have [SERVICE] section with Flush, Daemon, and Log_Level
    - Must have at least one [INPUT] and one [OUTPUT] section
    - OpenSearch output must have Logstash_Format for time-based indices
    - Suppress_Type_Name must be On for OpenSearch 2.x compatibility
    - Forward input must listen on expected port (24224)

Date: 2026-02-06
Severity: High
"""

import pytest
import re
from pathlib import Path


class TestRegressionFluentBitConfig:
    """Regression tests for Fluent Bit configuration"""

    @pytest.fixture
    def config_path(self):
        """Path to fluent-bit.conf"""
        return Path("ingestion/configs/fluent-bit/fluent-bit.conf")

    @pytest.fixture
    def config_content(self, config_path):
        """Read raw config file content"""
        with open(config_path, 'r') as f:
            return f.read()

    @pytest.fixture
    def active_sections(self, config_content):
        """Parse active (non-commented) sections from config"""
        sections = []
        current_section = None

        for line in config_content.split('\n'):
            stripped = line.strip()
            # Skip comments and empty lines
            if stripped.startswith('#') or not stripped:
                continue

            # Match section headers like [SERVICE], [INPUT], etc.
            section_match = re.match(r'^\[(\w+)\]', stripped)
            if section_match:
                current_section = {
                    'type': section_match.group(1),
                    'directives': {}
                }
                sections.append(current_section)
            elif current_section and '    ' in line and not stripped.startswith('#'):
                # Parse key-value directive
                parts = stripped.split(None, 1)
                if len(parts) == 2:
                    current_section['directives'][parts[0]] = parts[1]

        return sections

    def test_regression_007_has_service_section(self, active_sections):
        """Verify [SERVICE] section exists with required directives."""
        service_sections = [s for s in active_sections if s['type'] == 'SERVICE']
        assert len(service_sections) == 1, (
            "Fluent Bit config must have exactly one [SERVICE] section"
        )

        service = service_sections[0]['directives']
        assert 'Flush' in service, "SERVICE must define Flush interval"
        assert 'Daemon' in service, "SERVICE must define Daemon mode"
        assert 'Log_Level' in service, "SERVICE must define Log_Level"

    def test_regression_007_has_input_section(self, active_sections):
        """Verify at least one [INPUT] section exists."""
        input_sections = [s for s in active_sections if s['type'] == 'INPUT']
        assert len(input_sections) >= 1, (
            "Fluent Bit config must have at least one [INPUT] section"
        )

    def test_regression_007_has_output_section(self, active_sections):
        """Verify at least one [OUTPUT] section exists."""
        output_sections = [s for s in active_sections if s['type'] == 'OUTPUT']
        assert len(output_sections) >= 1, (
            "Fluent Bit config must have at least one [OUTPUT] section"
        )

    def test_regression_007_opensearch_output_has_logstash_format(self, active_sections):
        """
        Verify OpenSearch output uses Logstash_Format for time-based indices.
        Without this, all logs go to a single index instead of daily indices.
        """
        os_outputs = [
            s for s in active_sections
            if s['type'] == 'OUTPUT' and s['directives'].get('Name') == 'opensearch'
        ]
        assert len(os_outputs) >= 1, "Must have an OpenSearch output configured"

        for output in os_outputs:
            assert output['directives'].get('Logstash_Format') == 'On', (
                "OpenSearch output must have Logstash_Format On for time-based indices"
            )

    def test_regression_007_opensearch_suppress_type_name(self, active_sections):
        """
        Verify Suppress_Type_Name is On for OpenSearch 2.x compatibility.
        OpenSearch 2.x removed type support; without this setting,
        Fluent Bit sends _doc type which causes warnings or errors.
        """
        os_outputs = [
            s for s in active_sections
            if s['type'] == 'OUTPUT' and s['directives'].get('Name') == 'opensearch'
        ]

        for output in os_outputs:
            assert output['directives'].get('Suppress_Type_Name') == 'On', (
                "OpenSearch output must have Suppress_Type_Name On for 2.x compatibility"
            )

    def test_regression_007_forward_input_on_expected_port(self, active_sections):
        """
        Verify forward input listens on port 24224 (standard Fluent forward port).
        DRM integration guide and other docs reference this port.
        """
        forward_inputs = [
            s for s in active_sections
            if s['type'] == 'INPUT' and s['directives'].get('Name') == 'forward'
        ]
        assert len(forward_inputs) >= 1, "Must have a forward input for receiving events"

        for inp in forward_inputs:
            assert inp['directives'].get('Port') == '24224', (
                "Forward input must listen on port 24224 (standard forward protocol port)"
            )

    def test_regression_007_parsers_file_referenced(self, active_sections):
        """Verify SERVICE section references a parsers file."""
        service = [s for s in active_sections if s['type'] == 'SERVICE'][0]
        assert 'Parsers_File' in service['directives'], (
            "SERVICE must reference a Parsers_File for log parsing"
        )
