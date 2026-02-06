"""
Regression Test RT-005: Dashboard Panel References Must Match

Original Bug:
    OpenSearch Dashboards showed "Could not find reference 'panel_1'" errors
    when loading imported dashboards. The panelRefName values in panelsJSON
    did not match the reference name values in the references array.

    Example: Panel had panelRefName "panel_1" but reference had name "panel_0",
    causing the dashboard to fail to render panels.

How to Reproduce:
    1. Import dashboards.ndjson into OpenSearch Dashboards
    2. Open Operations Dashboard or Analytics Dashboard
    3. Panels fail to load with "Could not find reference" errors

Fix Applied:
    - Corrected reference naming in dashboards.ndjson
    - Ensured panelRefName in panelsJSON uses 0-based indexing (panel_0, panel_1, ...)
    - Ensured references array name field matches panelRefName exactly

Date: 2026-02-06
Severity: High
"""

import json
import pytest
from pathlib import Path


class TestRegressionDashboardPanelReferences:
    """Regression tests for dashboard panel reference issues"""

    @pytest.fixture
    def dashboards_ndjson_path(self):
        """Path to dashboards.ndjson"""
        return Path("dashboards/opensearch-dashboards/saved-objects/dashboards.ndjson")

    @pytest.fixture
    def dashboards(self, dashboards_ndjson_path):
        """Load all dashboard objects from ndjson"""
        dashboards = []
        with open(dashboards_ndjson_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    dashboards.append(json.loads(line))
        return dashboards

    def test_regression_005_panel_ref_names_match_references(self, dashboards):
        """
        Verify that every panelRefName in panelsJSON has a matching entry
        in the references array.

        This test would have failed before the fix when panel_1 references
        did not exist in the references array.
        """
        for dashboard in dashboards:
            title = dashboard["attributes"]["title"]
            panels = json.loads(dashboard["attributes"]["panelsJSON"])
            references = dashboard["references"]

            ref_names = {ref["name"] for ref in references}

            for panel in panels:
                panel_ref = panel["panelRefName"]
                assert panel_ref in ref_names, (
                    f"Dashboard '{title}': panelRefName '{panel_ref}' "
                    f"has no matching reference. Available: {ref_names}"
                )

    def test_regression_005_references_point_to_valid_visualizations(self, dashboards):
        """
        Verify that all dashboard references point to visualization IDs
        that follow the expected naming pattern.
        """
        for dashboard in dashboards:
            title = dashboard["attributes"]["title"]
            references = dashboard["references"]

            for ref in references:
                assert ref["type"] == "visualization", (
                    f"Dashboard '{title}': reference '{ref['name']}' "
                    f"has unexpected type '{ref['type']}', expected 'visualization'"
                )
                assert ref["id"].startswith("viz-"), (
                    f"Dashboard '{title}': reference '{ref['name']}' "
                    f"points to '{ref['id']}' which doesn't follow 'viz-*' naming"
                )

    def test_regression_005_panel_indices_are_sequential(self, dashboards):
        """
        Verify that panelRefName values use 0-based sequential indexing
        (panel_0, panel_1, panel_2, ...) to prevent reference mismatches.
        """
        for dashboard in dashboards:
            title = dashboard["attributes"]["title"]
            panels = json.loads(dashboard["attributes"]["panelsJSON"])

            for i, panel in enumerate(panels):
                expected_ref = f"panel_{i}"
                assert panel["panelRefName"] == expected_ref, (
                    f"Dashboard '{title}': panel {i} has panelRefName "
                    f"'{panel['panelRefName']}', expected '{expected_ref}'"
                )

    def test_regression_005_panel_count_matches_reference_count(self, dashboards):
        """
        Verify that the number of panels matches the number of references.
        A mismatch indicates orphaned panels or references.
        """
        for dashboard in dashboards:
            title = dashboard["attributes"]["title"]
            panels = json.loads(dashboard["attributes"]["panelsJSON"])
            references = dashboard["references"]

            assert len(panels) == len(references), (
                f"Dashboard '{title}': has {len(panels)} panels but "
                f"{len(references)} references. These must match."
            )
