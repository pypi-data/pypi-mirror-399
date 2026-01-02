"""Tests for scanner check command."""

from __future__ import annotations

import json
from unittest.mock import patch

import typer
from typer.testing import CliRunner

from iltero.commands.scanner.check import scanner_check

runner = CliRunner()


# Create a test app that wraps scanner_check for testing
test_app = typer.Typer()
test_app.command()(scanner_check)


class TestScannerCheck:
    """Tests for the scanner check command."""

    def test_check_all_available(self) -> None:
        """Test check when all scanners are available."""
        with (
            patch("iltero.commands.scanner.check.CheckovScanner") as mock_checkov,
            patch("iltero.commands.scanner.check.OPAScanner") as mock_opa,
            patch("iltero.commands.scanner.check.CloudCustodianScanner") as mock_custodian,
        ):
            # Set up mock scanners
            mock_checkov.return_value.is_available.return_value = True
            mock_checkov.return_value.get_version.return_value = "2.5.0"

            mock_opa.return_value.is_available.return_value = True
            mock_opa.return_value.get_version.return_value = "0.50.0"

            mock_custodian.return_value.is_available.return_value = True
            mock_custodian.return_value.get_version.return_value = "0.9.30"

            result = runner.invoke(test_app, [])

            assert result.exit_code == 0
            assert "Checkov" in result.output
            assert "OPA" in result.output
            assert "Cloud Custodian" in result.output
            assert "All scanners ready" in result.output

    def test_check_some_missing(self) -> None:
        """Test check when some scanners are missing."""
        with (
            patch("iltero.commands.scanner.check.CheckovScanner") as mock_checkov,
            patch("iltero.commands.scanner.check.OPAScanner") as mock_opa,
            patch("iltero.commands.scanner.check.CloudCustodianScanner") as mock_custodian,
        ):
            # Checkov available, OPA and Custodian missing
            mock_checkov.return_value.is_available.return_value = True
            mock_checkov.return_value.get_version.return_value = "2.5.0"

            mock_opa.return_value.is_available.return_value = False
            mock_opa.return_value.get_version.return_value = "unknown"

            mock_custodian.return_value.is_available.return_value = False
            mock_custodian.return_value.get_version.return_value = "unknown"

            result = runner.invoke(test_app, [])

            assert result.exit_code == 1
            assert "Installed" in result.output
            assert "Not Found" in result.output
            assert "Some scanners are not installed" in result.output

    def test_check_all_missing(self) -> None:
        """Test check when all scanners are missing."""
        with (
            patch("iltero.commands.scanner.check.CheckovScanner") as mock_checkov,
            patch("iltero.commands.scanner.check.OPAScanner") as mock_opa,
            patch("iltero.commands.scanner.check.CloudCustodianScanner") as mock_custodian,
        ):
            mock_checkov.return_value.is_available.return_value = False
            mock_opa.return_value.is_available.return_value = False
            mock_custodian.return_value.is_available.return_value = False

            result = runner.invoke(test_app, [])

            assert result.exit_code == 1
            assert "Not Found" in result.output

    def test_check_verbose_shows_instructions(self) -> None:
        """Test verbose flag shows installation instructions."""
        with (
            patch("iltero.commands.scanner.check.CheckovScanner") as mock_checkov,
            patch("iltero.commands.scanner.check.OPAScanner") as mock_opa,
            patch("iltero.commands.scanner.check.CloudCustodianScanner") as mock_custodian,
        ):
            mock_checkov.return_value.is_available.return_value = False
            mock_opa.return_value.is_available.return_value = False
            mock_custodian.return_value.is_available.return_value = False

            result = runner.invoke(test_app, ["--verbose"])

            assert result.exit_code == 1
            assert "Installation Instructions" in result.output
            assert "pip install checkov" in result.output
            assert "brew install opa" in result.output
            assert "pip install c7n" in result.output

    def test_check_json_output(self) -> None:
        """Test JSON output format."""
        with (
            patch("iltero.commands.scanner.check.CheckovScanner") as mock_checkov,
            patch("iltero.commands.scanner.check.OPAScanner") as mock_opa,
            patch("iltero.commands.scanner.check.CloudCustodianScanner") as mock_custodian,
        ):
            mock_checkov.return_value.is_available.return_value = True
            mock_checkov.return_value.get_version.return_value = "2.5.0"

            mock_opa.return_value.is_available.return_value = True
            mock_opa.return_value.get_version.return_value = "0.50.0"

            mock_custodian.return_value.is_available.return_value = True
            mock_custodian.return_value.get_version.return_value = "0.9.30"

            result = runner.invoke(test_app, ["--json"])

            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["all_available"] is True
            assert len(data["scanners"]) == 3
            assert data["scanners"][0]["name"] == "Checkov"
            assert data["scanners"][0]["available"] is True
            assert data["scanners"][0]["version"] == "2.5.0"

    def test_check_json_output_with_missing(self) -> None:
        """Test JSON output format when scanners are missing."""
        with (
            patch("iltero.commands.scanner.check.CheckovScanner") as mock_checkov,
            patch("iltero.commands.scanner.check.OPAScanner") as mock_opa,
            patch("iltero.commands.scanner.check.CloudCustodianScanner") as mock_custodian,
        ):
            mock_checkov.return_value.is_available.return_value = True
            mock_checkov.return_value.get_version.return_value = "2.5.0"

            mock_opa.return_value.is_available.return_value = False

            mock_custodian.return_value.is_available.return_value = False

            result = runner.invoke(test_app, ["--json"])

            assert result.exit_code == 1
            data = json.loads(result.output)
            assert data["all_available"] is False
            assert data["scanners"][0]["available"] is True
            assert data["scanners"][1]["available"] is False
            assert data["scanners"][2]["available"] is False

    def test_check_displays_command_mapping(self) -> None:
        """Test that scanner check shows which commands use each scanner."""
        with (
            patch("iltero.commands.scanner.check.CheckovScanner") as mock_checkov,
            patch("iltero.commands.scanner.check.OPAScanner") as mock_opa,
            patch("iltero.commands.scanner.check.CloudCustodianScanner") as mock_custodian,
        ):
            mock_checkov.return_value.is_available.return_value = True
            mock_checkov.return_value.get_version.return_value = "2.5.0"

            mock_opa.return_value.is_available.return_value = True
            mock_opa.return_value.get_version.return_value = "0.50.0"

            mock_custodian.return_value.is_available.return_value = True
            mock_custodian.return_value.get_version.return_value = "0.9.30"

            result = runner.invoke(test_app, [])

            assert result.exit_code == 0
            assert "scan static" in result.output
            assert "scan evaluation" in result.output
            assert "scan runtime" in result.output
