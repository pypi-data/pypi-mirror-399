"""Compliance commands for violations, policies, scans, and remediation."""

from __future__ import annotations

import typer

from iltero.commands.compliance.assessment import app as assessment_app
from iltero.commands.compliance.evidence import app as evidence_app
from iltero.commands.compliance.manifests import app as manifests_app
from iltero.commands.compliance.monitoring import app as monitoring_app
from iltero.commands.compliance.policy import app as policy_app
from iltero.commands.compliance.policy_sets import app as policy_sets_app
from iltero.commands.compliance.remediation import app as remediation_app
from iltero.commands.compliance.reports import app as reports_app
from iltero.commands.compliance.scans import app as scans_app
from iltero.commands.compliance.violations import app as violations_app

# Create main compliance app
app = typer.Typer(help="Compliance management commands")

# Register sub-commands
app.add_typer(violations_app, name="violations", help="Compliance violations")
app.add_typer(policy_app, name="policy", help="Compliance policies")
app.add_typer(policy_sets_app, name="policy-sets", help="Policy sets")
app.add_typer(scans_app, name="scans", help="Compliance scans")
app.add_typer(remediation_app, name="remediation", help="Remediation actions")
app.add_typer(reports_app, name="reports", help="Compliance reports")
app.add_typer(assessment_app, name="assessment", help="Compliance assessment")
app.add_typer(monitoring_app, name="monitoring", help="Compliance monitoring")
app.add_typer(evidence_app, name="evidence", help="Compliance evidence")
app.add_typer(manifests_app, name="manifest", help="Compliance manifests")

__all__ = ["app"]
