# Copyright 2025 Tenro.ai
# SPDX-License-Identifier: Apache-2.0

"""JSON artifact exporter for capability reports.

Exports reports to .tenro/artifacts/ for CI/CD integration and pytest-xdist
worker merging.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tenro.capabilities.reporting import merge_reports
from tenro.capabilities.types import CapabilityReport


class ArtifactExporter:
    """Export capability reports to JSON artifacts.

    Supports:
    - Capabilities export (declared, presented, executed)
    - Coverage export (metrics, security smells)
    - pytest-xdist worker suffixing and merging

    Attributes:
        output_dir: Output directory for artifact files.
        _worker_id: Optional pytest-xdist worker suffix.
    """

    DEFAULT_OUTPUT_DIR = ".tenro/artifacts"

    def __init__(
        self,
        output_dir: Path | None = None,
        worker_id: str | None = None,
    ) -> None:
        """Initialize exporter.

        Args:
            output_dir: Directory for output files. Default: .tenro/artifacts/
            worker_id: pytest-xdist worker ID for suffixing (e.g., "gw0").
        """
        self._output_dir = Path(output_dir) if output_dir else Path(self.DEFAULT_OUTPUT_DIR)
        self._worker_id = worker_id

    @property
    def output_dir(self) -> Path:
        """Get output directory.

        Returns:
            Export output directory.
        """
        return self._output_dir

    @staticmethod
    def _timestamp() -> str:
        """Return UTC timestamp in ISO-8601 format."""
        return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _strip_timestamp(data: dict[str, Any]) -> dict[str, Any]:
        """Return copy with timestamp removed for model validation."""
        stripped = dict(data)
        stripped.pop("timestamp", None)
        return stripped

    def _ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def _get_filename(self, base_name: str) -> str:
        """Get filename with optional worker suffix."""
        if self._worker_id:
            return f"{base_name}.{self._worker_id}.json"
        return f"{base_name}.json"

    def export_capabilities(self, report: CapabilityReport) -> Path:
        """Export full capability report to JSON.

        Args:
            report: CapabilityReport to export.

        Returns:
            Path to exported file.
        """
        self._ensure_output_dir()

        filename = self._get_filename("capabilities")
        path = self._output_dir / filename

        data = report.model_dump(mode="json")
        data["timestamp"] = self._timestamp()
        self._write_json(path, data)

        return path

    def export_coverage(self, report: CapabilityReport) -> Path:
        """Export coverage-focused report to JSON.

        Args:
            report: CapabilityReport to export (extracts coverage metrics).

        Returns:
            Path to exported file.
        """
        self._ensure_output_dir()

        filename = self._get_filename("coverage")
        path = self._output_dir / filename

        # Extract coverage-specific data
        data = {
            "agents": [a.model_dump(mode="json") for a in report.agents],
            "security": report.security.model_dump(mode="json"),
            "observability": report.observability.model_dump(mode="json"),
        }
        data["timestamp"] = self._timestamp()
        self._write_json(path, data)

        return path

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        """Write JSON with sorted keys for diff-friendly output."""
        path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))

    @classmethod
    def merge_worker_artifacts(cls, artifact_paths: list[Path], output_path: Path) -> Path:
        """Merge multiple worker artifacts into single report.

        Used by pytest-xdist controller to combine worker results.

        Args:
            artifact_paths: Paths to worker artifact files.
            output_path: Path for merged output.

        Returns:
            Path to merged file.
        """
        reports = [
            CapabilityReport.model_validate(cls._strip_timestamp(json.loads(path.read_text())))
            for path in artifact_paths
        ]
        merged = merge_reports(reports)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = merged.model_dump(mode="json")
        data["timestamp"] = cls._timestamp()
        output_path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))

        return output_path
