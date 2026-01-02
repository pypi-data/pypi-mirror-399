"""Configuration and fixtures for E2E tests."""

import os

import pytest


def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption(
        "--e2e",
        action="store_true",
        default=False,
        help="Run E2E tests (requires real backend)",
    )
    parser.addoption(
        "--backend-url",
        action="store",
        default=os.getenv("ILTERO_BACKEND_URL", "https://staging.iltero.com"),
        help="Backend URL for E2E tests",
    )
    parser.addoption(
        "--test-token",
        action="store",
        default=os.getenv("ILTERO_TEST_TOKEN"),
        help="Authentication token for E2E tests",
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "e2e: mark test as end-to-end test (requires --e2e flag)",
    )


def pytest_collection_modifyitems(config, items):
    """Skip E2E tests unless --e2e flag is provided."""
    if config.getoption("--e2e"):
        return

    skip_e2e = pytest.mark.skip(reason="need --e2e option to run")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)


@pytest.fixture(scope="session")
def backend_url(request):
    """Get backend URL from config."""
    return request.config.getoption("--backend-url")


@pytest.fixture(scope="session")
def test_token(request):
    """Get test authentication token."""
    token = request.config.getoption("--test-token")
    if not token:
        pytest.skip("Test token not provided (use --test-token or ILTERO_TEST_TOKEN)")
    return token


@pytest.fixture(scope="session")
def check_backend_available(backend_url):
    """Check if backend is available before running tests."""
    import httpx

    try:
        response = httpx.get(f"{backend_url}/health", timeout=5.0)
        if response.status_code != 200:
            pytest.skip(f"Backend at {backend_url} not available")
    except Exception as e:
        pytest.skip(f"Cannot connect to backend at {backend_url}: {e}")


@pytest.fixture(scope="session")
def check_scanners_installed():
    """Check if required scanners are installed."""
    import shutil

    scanners = {
        "checkov": shutil.which("checkov"),
        "opa": shutil.which("opa"),
    }

    missing = [name for name, path in scanners.items() if path is None]
    if missing:
        pytest.skip(f"Required scanners not installed: {', '.join(missing)}")

    return scanners


@pytest.fixture
def e2e_config_dir(tmp_path, test_token, backend_url):
    """Create a temporary config directory for E2E tests."""
    config_dir = tmp_path / ".iltero"
    config_dir.mkdir()

    # Write config file
    config_file = config_dir / "config.yaml"
    config_file.write_text(f"""
api_url: {backend_url}
token: {test_token}
output_format: json
""")

    return config_dir


@pytest.fixture
def terraform_test_project(tmp_path):
    """Create a real Terraform project for testing."""
    project_dir = tmp_path / "terraform-test"
    project_dir.mkdir()

    # Create main.tf with intentional policy violations
    main_tf = project_dir / "main.tf"
    main_tf.write_text("""
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# S3 bucket without encryption - should fail policies
resource "aws_s3_bucket" "test_bucket" {
  bucket = "iltero-e2e-test-bucket-${formatdate("YYYYMMDDhhmmss", timestamp())}"

  tags = {
    Environment = "test"
    ManagedBy   = "iltero-cli-e2e"
  }
}

# S3 bucket with encryption - should pass
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "iltero-e2e-secure-bucket-${formatdate("YYYYMMDDhhmmss", timestamp())}"

  tags = {
    Environment = "test"
    ManagedBy   = "iltero-cli-e2e"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "secure_bucket" {
  bucket = aws_s3_bucket.secure_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# EC2 instance without IMDSv2 - should fail policies
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2 AMI
  instance_type = "t2.micro"

  tags = {
    Name        = "iltero-e2e-test"
    Environment = "test"
    ManagedBy   = "iltero-cli-e2e"
  }
}
""")

    # Create variables.tf
    variables_tf = project_dir / "variables.tf"
    variables_tf.write_text("""
variable "environment" {
  type        = string
  description = "Environment name"
  default     = "test"
}

variable "region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}
""")

    # Create outputs.tf
    outputs_tf = project_dir / "outputs.tf"
    outputs_tf.write_text("""
output "test_bucket_id" {
  description = "Test bucket ID"
  value       = aws_s3_bucket.test_bucket.id
}

output "secure_bucket_id" {
  description = "Secure bucket ID"
  value       = aws_s3_bucket.secure_bucket.id
}
""")

    return project_dir
