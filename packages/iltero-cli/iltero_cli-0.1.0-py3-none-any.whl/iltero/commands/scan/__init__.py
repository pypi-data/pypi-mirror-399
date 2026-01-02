"""Scan commands for compliance scanning."""

from __future__ import annotations

from iltero.commands.scan.evaluation import scan_evaluation
from iltero.commands.scan.main import (
    EXIT_API_ERROR,
    EXIT_CONFIG_ERROR,
    EXIT_SCAN_FAILED,
    EXIT_SCANNER_ERROR,
    EXIT_SUCCESS,
    app,
    console,
    print_scan_summary,
    print_violations,
    save_results,
    severity_from_string,
    upload_apply_results,
    upload_plan_results,
    upload_results,
)
from iltero.commands.scan.runtime import scan_runtime
from iltero.commands.scan.static import scan_static
from iltero.commands.scan.status import scan_list, scan_status
from iltero.commands.scan.submit_results import submit_results

# Register commands
app.command("static")(scan_static)
app.command("evaluation")(scan_evaluation)
app.command("runtime")(scan_runtime)
app.command("status")(scan_status)
app.command("list")(scan_list)
app.command("submit-results")(submit_results)

__all__ = [
    "app",
    "console",
    "scan_static",
    "scan_evaluation",
    "scan_runtime",
    "scan_status",
    "scan_list",
    "submit_results",
    "severity_from_string",
    "print_scan_summary",
    "print_violations",
    "save_results",
    "upload_results",
    "upload_plan_results",
    "upload_apply_results",
    "EXIT_SUCCESS",
    "EXIT_SCAN_FAILED",
    "EXIT_CONFIG_ERROR",
    "EXIT_API_ERROR",
    "EXIT_SCANNER_ERROR",
]
