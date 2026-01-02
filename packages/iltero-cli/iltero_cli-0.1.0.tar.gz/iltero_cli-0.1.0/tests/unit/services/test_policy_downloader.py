"""Tests for PolicyArtifactDownloader service."""

import hashlib
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from iltero.services.models import PolicyArtifact, PolicySource
from iltero.services.policy_downloader import (
    PolicyArtifactDownloader,
    PolicyDownloadError,
    PolicyIntegrityError,
)


class TestPolicyIntegrityError:
    """Test PolicyIntegrityError exception."""

    def test_error_message(self):
        """Test error message formatting."""
        error = PolicyIntegrityError(
            artifact_key="test/policy",
            expected="abc123",
            actual="def456",
        )

        assert "test/policy" in str(error)
        assert "abc123" in str(error)
        assert "def456" in str(error)
        assert error.exit_code == 10


class TestPolicyDownloadError:
    """Test PolicyDownloadError exception."""

    def test_error_message(self):
        """Test error message formatting."""
        error = PolicyDownloadError(
            artifact_key="failed/policy",
            message="Connection refused",
        )

        assert "failed/policy" in str(error)
        assert "Connection refused" in str(error)
        assert error.exit_code == 11


class TestPolicyArtifactDownloader:
    """Test PolicyArtifactDownloader class."""

    def test_init_default_cache_dir(self):
        """Test default cache directory."""
        downloader = PolicyArtifactDownloader()

        assert downloader.cache_dir == Path(".iltero") / "policy_cache"

    def test_init_custom_cache_dir(self):
        """Test custom cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / "custom_cache"
            downloader = PolicyArtifactDownloader(cache_dir=cache_dir)

            assert downloader.cache_dir == cache_dir

    def test_compute_sha256(self):
        """Test SHA256 computation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "test.txt"
            test_content = b"test content for hashing"
            test_file.write_bytes(test_content)

            # Compute expected hash
            expected_hash = hashlib.sha256(test_content).hexdigest()

            # Test computation
            downloader = PolicyArtifactDownloader()
            actual_hash = downloader._compute_sha256(test_file)

            assert actual_hash == expected_hash

    def test_get_cache_path_with_sha256(self):
        """Test cache path generation with SHA256."""
        downloader = PolicyArtifactDownloader(
            cache_dir=Path("/tmp/cache"),
        )

        artifact = PolicyArtifact(
            key="security/encryption",
            source=PolicySource.BUNDLE,
            required=True,
            artifact_sha256="abc123def456",
        )

        cache_path = downloader._get_cache_path(artifact)

        assert cache_path == Path("/tmp/cache/abc123def456/security/encryption.rego")

    def test_get_cache_path_without_sha256(self):
        """Test cache path generation without SHA256."""
        downloader = PolicyArtifactDownloader(
            cache_dir=Path("/tmp/cache"),
        )

        artifact = PolicyArtifact(
            key="unverified/policy",
            source=PolicySource.ORG,
            required=False,
        )

        cache_path = downloader._get_cache_path(artifact)

        assert cache_path == Path("/tmp/cache/unverified/unverified/policy.rego")

    def test_is_cached_file_not_exists(self):
        """Test is_cached when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = PolicyArtifactDownloader(cache_dir=Path(tmpdir))

            artifact = PolicyArtifact(
                key="missing/policy",
                source=PolicySource.BUNDLE,
                required=True,
                artifact_sha256="somehash",
            )

            assert downloader.is_cached(artifact) is False

    def test_is_cached_file_exists_valid(self):
        """Test is_cached when file exists and hash matches."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            downloader = PolicyArtifactDownloader(cache_dir=cache_dir)

            # Create cached file
            content = b"policy content"
            content_hash = hashlib.sha256(content).hexdigest()

            cache_path = cache_dir / content_hash / "test/policy.rego"
            cache_path.parent.mkdir(parents=True)
            cache_path.write_bytes(content)

            artifact = PolicyArtifact(
                key="test/policy",
                source=PolicySource.BUNDLE,
                required=True,
                artifact_sha256=content_hash,
            )

            assert downloader.is_cached(artifact) is True

    def test_is_cached_file_exists_invalid_hash(self):
        """Test is_cached when file exists but hash doesn't match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            downloader = PolicyArtifactDownloader(cache_dir=cache_dir)

            # Create cached file with wrong content
            wrong_hash = "wronghash123"
            cache_path = cache_dir / wrong_hash / "test/policy.rego"
            cache_path.parent.mkdir(parents=True)
            cache_path.write_bytes(b"wrong content")

            artifact = PolicyArtifact(
                key="test/policy",
                source=PolicySource.BUNDLE,
                required=True,
                artifact_sha256=wrong_hash,
            )

            # Hash won't match the file content
            assert downloader.is_cached(artifact) is False

    def test_download_artifact_no_uri(self):
        """Test download fails when no URI provided."""
        downloader = PolicyArtifactDownloader()

        artifact = PolicyArtifact(
            key="no/uri",
            source=PolicySource.BUNDLE,
            required=True,
            artifact_uri=None,
        )

        with pytest.raises(PolicyDownloadError) as exc_info:
            downloader.download_artifact(artifact)

        assert "No artifact URI provided" in str(exc_info.value)

    def test_download_artifact_uses_cache(self):
        """Test download returns cached file when valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            downloader = PolicyArtifactDownloader(cache_dir=cache_dir)

            # Create cached file
            content = b"cached policy"
            content_hash = hashlib.sha256(content).hexdigest()

            cache_path = cache_dir / content_hash / "cached/policy.rego"
            cache_path.parent.mkdir(parents=True)
            cache_path.write_bytes(content)

            artifact = PolicyArtifact(
                key="cached/policy",
                source=PolicySource.BUNDLE,
                required=True,
                artifact_uri="https://example.com/policy.rego",
                artifact_sha256=content_hash,
            )

            # Should return cached path without making HTTP request
            path, sha256 = downloader.download_artifact(artifact)

            assert path == cache_path
            assert sha256 == content_hash

    @patch("iltero.services.policy_downloader.httpx.Client")
    def test_download_artifact_success(self, mock_client_class):
        """Test successful artifact download."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            downloader = PolicyArtifactDownloader(cache_dir=cache_dir)

            # Mock HTTP response
            content = b"downloaded policy content"
            content_hash = hashlib.sha256(content).hexdigest()

            mock_response = Mock()
            mock_response.content = content
            mock_response.raise_for_status = Mock()

            mock_client = Mock()
            mock_client.get.return_value = mock_response
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            artifact = PolicyArtifact(
                key="download/test",
                source=PolicySource.BUNDLE,
                required=True,
                artifact_uri="https://example.com/policy.rego",
                artifact_sha256=content_hash,
            )

            path, sha256 = downloader.download_artifact(artifact, force=True)

            assert path.exists()
            assert sha256 == content_hash
            assert path.read_bytes() == content

    @patch("iltero.services.policy_downloader.httpx.Client")
    def test_download_artifact_integrity_error(self, mock_client_class):
        """Test download fails when SHA256 doesn't match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            downloader = PolicyArtifactDownloader(cache_dir=cache_dir)

            # Mock HTTP response with wrong content
            mock_response = Mock()
            mock_response.content = b"wrong content"
            mock_response.raise_for_status = Mock()

            mock_client = Mock()
            mock_client.get.return_value = mock_response
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client_class.return_value = mock_client

            artifact = PolicyArtifact(
                key="integrity/test",
                source=PolicySource.BUNDLE,
                required=True,
                artifact_uri="https://example.com/policy.rego",
                artifact_sha256="expected_but_wrong_hash",
            )

            with pytest.raises(PolicyIntegrityError):
                downloader.download_artifact(artifact, force=True)

    def test_download_artifacts_multiple(self):
        """Test downloading multiple artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            downloader = PolicyArtifactDownloader(cache_dir=cache_dir)

            # Create cached files
            artifacts = []
            for i in range(3):
                content = f"policy {i}".encode()
                content_hash = hashlib.sha256(content).hexdigest()

                cache_path = cache_dir / content_hash / f"policy{i}.rego"
                cache_path.parent.mkdir(parents=True)
                cache_path.write_bytes(content)

                artifacts.append(
                    PolicyArtifact(
                        key=f"policy{i}",
                        source=PolicySource.BUNDLE,
                        required=True,
                        artifact_uri=f"https://example.com/policy{i}.rego",
                        artifact_sha256=content_hash,
                    )
                )

            results = downloader.download_artifacts(artifacts)

            assert len(results) == 3
            for key in ["policy0", "policy1", "policy2"]:
                assert key in results

    def test_download_artifacts_skips_no_uri(self):
        """Test download_artifacts skips artifacts without URI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = PolicyArtifactDownloader(cache_dir=Path(tmpdir))

            artifacts = [
                PolicyArtifact(
                    key="no-uri",
                    source=PolicySource.BUNDLE,
                    required=False,
                    artifact_uri=None,
                ),
            ]

            results = downloader.download_artifacts(artifacts)

            assert len(results) == 0

    def test_get_artifact_paths(self):
        """Test extracting paths from download results."""
        downloader = PolicyArtifactDownloader()

        downloaded = {
            "policy1": (Path("/cache/policy1.rego"), "hash1"),
            "policy2": (Path("/cache/policy2.rego"), "hash2"),
        }

        paths = downloader.get_artifact_paths(downloaded)

        assert len(paths) == 2
        assert Path("/cache/policy1.rego") in paths
        assert Path("/cache/policy2.rego") in paths

    def test_get_artifact_sha256s(self):
        """Test extracting SHA256s from download results."""
        downloader = PolicyArtifactDownloader()

        downloaded = {
            "policy1": (Path("/cache/policy1.rego"), "hash1"),
            "policy2": (Path("/cache/policy2.rego"), "hash2"),
        }

        sha256s = downloader.get_artifact_sha256s(downloaded)

        assert sha256s == {"policy1": "hash1", "policy2": "hash2"}
