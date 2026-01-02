"""CI/CD context detection for audit trail and evidence collection.

This package provides automatic detection and collection of CI/CD pipeline
context from environment variables across multiple providers.

Supports:
- GitHub Actions
- GitLab CI
- Bitbucket Pipelines
- Azure DevOps
- Jenkins
- CircleCI

Used for SOC 2 / ISO 27001 compliance evidence collection.
"""

from __future__ import annotations

from .detector import detect_cicd_context, get_provider_name, is_ci_environment

__all__ = ["detect_cicd_context", "get_provider_name", "is_ci_environment"]
