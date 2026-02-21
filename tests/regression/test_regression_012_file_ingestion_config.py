"""
Regression Test RT-012: File-Based Ingestion Configuration Validation

Validates that Fluent Bit is properly configured for file-based log
ingestion and that docker-compose.yml mounts the shared logs directory.

Severity: Medium
Category: Ingestion Pipeline
Authors: Balaji Rajan and Claude (Anthropic)
"""

import re
from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FLUENT_BIT_CONF = PROJECT_ROOT / "ingestion" / "configs" / "fluent-bit" / "fluent-bit.conf"
PARSERS_CONF = PROJECT_ROOT / "ingestion" / "configs" / "fluent-bit" / "parsers.conf"
DOCKER_COMPOSE = PROJECT_ROOT / "docker-compose.yml"
SAMPLE_LOGS_DIR = PROJECT_ROOT / "ingestion" / "sample-logs"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def fluent_bit_config():
    """Load Fluent Bit configuration."""
    assert FLUENT_BIT_CONF.exists(), f"Fluent Bit config not found: {FLUENT_BIT_CONF}"
    return FLUENT_BIT_CONF.read_text(encoding="utf-8")


@pytest.fixture
def parsers_config():
    """Load parsers configuration."""
    assert PARSERS_CONF.exists(), f"Parsers config not found: {PARSERS_CONF}"
    return PARSERS_CONF.read_text(encoding="utf-8")


@pytest.fixture
def docker_compose_config():
    """Load docker-compose.yml."""
    assert DOCKER_COMPOSE.exists(), f"docker-compose.yml not found: {DOCKER_COMPOSE}"
    return DOCKER_COMPOSE.read_text(encoding="utf-8")


# ============================================================================
# Tests: Fluent Bit Tail Input Configuration
# ============================================================================

class TestFluentBitTailInput:
    """Validate Fluent Bit has tail input sections for file-based ingestion."""

    def test_has_tail_input_for_log_files(self, fluent_bit_config):
        """RT-012-01: Config must have a tail input for .log files."""
        assert "Name              tail" in fluent_bit_config, \
            "Fluent Bit config missing tail input plugin"
        assert "/app/logs/*.log" in fluent_bit_config, \
            "Tail input missing path for .log files (/app/logs/*.log)"

    def test_has_tail_input_for_txt_files(self, fluent_bit_config):
        """RT-012-02: Config must have a tail input for .txt files."""
        assert "/app/logs/*.txt" in fluent_bit_config, \
            "Tail input missing path for .txt files (/app/logs/*.txt)"

    def test_tail_uses_app_json_parser(self, fluent_bit_config):
        """RT-012-03: JSON tail input must use app_json parser."""
        # Find the section for .log files and check its parser
        log_section = fluent_bit_config.split("/app/logs/*.log")[0].rsplit("[INPUT]", 1)[-1]
        full_section = log_section + fluent_bit_config.split("/app/logs/*.log")[1].split("[")[0]
        assert "app_json" in full_section, \
            "Tail input for .log files must use app_json parser"

    def test_tail_uses_app_structured_parser(self, fluent_bit_config):
        """RT-012-04: Text tail input must use app_structured parser."""
        txt_section = fluent_bit_config.split("/app/logs/*.txt")[0].rsplit("[INPUT]", 1)[-1]
        full_section = txt_section + fluent_bit_config.split("/app/logs/*.txt")[1].split("[")[0]
        assert "app_structured" in full_section, \
            "Tail input for .txt files must use app_structured parser"

    def test_tail_reads_from_head(self, fluent_bit_config):
        """RT-012-05: Tail inputs should read from head for initial ingestion."""
        assert "Read_from_Head    True" in fluent_bit_config, \
            "Tail input should have Read_from_Head set to True"

    def test_tail_has_db_tracking(self, fluent_bit_config):
        """RT-012-06: Tail inputs must have DB files for position tracking."""
        assert "DB                /tmp/flb_file_json.db" in fluent_bit_config, \
            "JSON tail input missing DB file for position tracking"
        assert "DB                /tmp/flb_file_structured.db" in fluent_bit_config, \
            "Structured tail input missing DB file for position tracking"

    def test_tail_has_memory_buffer_limit(self, fluent_bit_config):
        """RT-012-07: Tail inputs must have memory buffer limits."""
        # Count Mem_Buf_Limit occurrences in tail sections
        tail_sections = fluent_bit_config.split("[INPUT]")
        file_sections = [s for s in tail_sections if "/app/logs/" in s]
        for section in file_sections:
            assert "Mem_Buf_Limit" in section, \
                "File tail input missing Mem_Buf_Limit configuration"


# ============================================================================
# Tests: Parser Existence
# ============================================================================

class TestParsersExist:
    """Validate that parsers referenced by tail inputs exist in parsers.conf."""

    def test_app_json_parser_exists(self, parsers_config):
        """RT-012-08: parsers.conf must define app_json parser."""
        assert re.search(r"Name\s+app_json", parsers_config), \
            "parsers.conf missing app_json parser definition"

    def test_app_structured_parser_exists(self, parsers_config):
        """RT-012-09: parsers.conf must define app_structured parser."""
        assert re.search(r"Name\s+app_structured", parsers_config), \
            "parsers.conf missing app_structured parser definition"

    def test_app_json_is_json_format(self, parsers_config):
        """RT-012-10: app_json parser must use JSON format."""
        # Extract section after app_json name
        match = re.search(r"Name\s+app_json.*?(?=\[PARSER\]|\Z)", parsers_config, re.DOTALL)
        assert match, "Could not find app_json parser section"
        assert "Format      json" in match.group(), \
            "app_json parser must use JSON format"

    def test_app_structured_is_regex_format(self, parsers_config):
        """RT-012-11: app_structured parser must use regex format."""
        match = re.search(r"Name\s+app_structured.*?(?=\[PARSER\]|\Z)", parsers_config, re.DOTALL)
        assert match, "Could not find app_structured parser section"
        assert "Format      regex" in match.group(), \
            "app_structured parser must use regex format"


# ============================================================================
# Tests: Docker Compose Volume Mount
# ============================================================================

class TestDockerComposeMount:
    """Validate docker-compose.yml mounts the sample-logs directory."""

    def test_fluent_bit_has_app_logs_volume(self, docker_compose_config):
        """RT-012-12: Fluent Bit service must mount sample-logs to /app/logs."""
        assert "/app/logs" in docker_compose_config, \
            "docker-compose.yml missing volume mount for /app/logs"

    def test_volume_mount_is_readonly(self, docker_compose_config):
        """RT-012-13: Sample logs volume should be mounted read-only."""
        assert "sample-logs:/app/logs:ro" in docker_compose_config, \
            "Sample logs volume mount should be read-only (:ro)"

    def test_mount_references_correct_host_path(self, docker_compose_config):
        """RT-012-14: Volume mount should reference ingestion/sample-logs."""
        assert "./ingestion/sample-logs:/app/logs" in docker_compose_config, \
            "Volume mount should reference ./ingestion/sample-logs"


# ============================================================================
# Tests: Sample Logs Directory
# ============================================================================

class TestSampleLogsDirectory:
    """Validate the sample-logs directory structure."""

    def test_sample_logs_directory_exists(self):
        """RT-012-15: ingestion/sample-logs/ directory must exist."""
        assert SAMPLE_LOGS_DIR.exists(), \
            f"Sample logs directory not found: {SAMPLE_LOGS_DIR}"

    def test_readme_exists(self):
        """RT-012-16: Sample logs directory must have a README."""
        readme = SAMPLE_LOGS_DIR / "README.md"
        assert readme.exists(), "ingestion/sample-logs/README.md not found"

    def test_sample_log_file_exists(self):
        """RT-012-17: At least one sample .log file must exist."""
        log_files = list(SAMPLE_LOGS_DIR.glob("*.log"))
        assert len(log_files) > 0, "No sample .log files found in ingestion/sample-logs/"

    def test_sample_log_is_valid_json_lines(self):
        """RT-012-18: Sample .log files must contain valid JSON lines."""
        import json
        for log_file in SAMPLE_LOGS_DIR.glob("*.log"):
            lines = log_file.read_text(encoding="utf-8").strip().split("\n")
            for i, line in enumerate(lines):
                try:
                    data = json.loads(line)
                    assert "timestamp" in data, f"Line {i+1} in {log_file.name} missing 'timestamp' field"
                    assert "level" in data, f"Line {i+1} in {log_file.name} missing 'level' field"
                    assert "message" in data, f"Line {i+1} in {log_file.name} missing 'message' field"
                except json.JSONDecodeError:
                    pytest.fail(f"Line {i+1} in {log_file.name} is not valid JSON: {line[:80]}")
