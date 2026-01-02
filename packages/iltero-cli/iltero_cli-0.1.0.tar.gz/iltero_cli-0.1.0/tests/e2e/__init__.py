"""End-to-end tests against real backend.

These tests require:
- Real Iltero backend running (staging/test environment)
- Valid authentication token
- Real scanners installed (checkov, opa)
- Network connectivity

Run with: pytest tests/e2e/ --e2e
Skip with: pytest (without --e2e flag)
"""
