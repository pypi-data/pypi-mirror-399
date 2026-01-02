"""Policy artifact downloader with SHA256 verification."""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import TYPE_CHECKING

import httpx

from iltero.core.exceptions import IlteroError

if TYPE_CHECKING:
    from iltero.services.models import PolicyArtifact
    from iltero.services.state_manager import ScanRunState


class PolicyIntegrityError(IlteroError):
    """Policy artifact failed SHA256 verification."""

    def __init__(self, artifact_key: str, expected: str, actual: str):
        message = (
            f"SHA256 mismatch for artifact '{artifact_key}': expected {expected}, got {actual}"
        )
        super().__init__(message, exit_code=10)
        self.artifact_key = artifact_key
        self.expected = expected
        self.actual = actual


class PolicyDownloadError(IlteroError):
    """Failed to download policy artifact."""

    def __init__(self, artifact_key: str, message: str):
        full_message = f"Failed to download artifact '{artifact_key}': {message}"
        super().__init__(full_message, exit_code=11)
        self.artifact_key = artifact_key


class PolicyArtifactDownloader:
    """Downloads and verifies policy artifacts.

    This service:
    1. Downloads policy artifacts from presigned S3 URLs
    2. Verifies SHA256 hashes for integrity
    3. Caches artifacts locally to avoid re-downloads
    4. Handles retries with exponential backoff
    """

    def __init__(
        self,
        cache_dir: Path | None = None,
        max_retries: int = 3,
        timeout: float = 60.0,
    ):
        """Initialize the artifact downloader.

        Args:
            cache_dir: Directory to cache artifacts. Defaults to .iltero/policy_cache
            max_retries: Maximum retry attempts for failed downloads.
            timeout: Download timeout in seconds.
        """
        self.cache_dir = cache_dir or Path(".iltero") / "policy_cache"
        self.max_retries = max_retries
        self.timeout = timeout

    def _compute_sha256(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _get_cache_path(self, artifact: PolicyArtifact) -> Path:
        """Get the cache path for an artifact.

        Uses SHA256 as directory name to enable content-addressable caching.
        """
        if artifact.artifact_sha256:
            return self.cache_dir / artifact.artifact_sha256 / f"{artifact.key}.rego"
        return self.cache_dir / "unverified" / f"{artifact.key}.rego"

    def is_cached(self, artifact: PolicyArtifact) -> bool:
        """Check if artifact is already cached and valid.

        Args:
            artifact: The policy artifact to check.

        Returns:
            True if cached and SHA256 matches, False otherwise.
        """
        cache_path = self._get_cache_path(artifact)
        if not cache_path.exists():
            return False

        if artifact.artifact_sha256:
            actual_sha256 = self._compute_sha256(cache_path)
            return actual_sha256 == artifact.artifact_sha256

        return True

    def _download_with_retry(
        self,
        url: str,
        dest_path: Path,
        artifact_key: str,
    ) -> None:
        """Download a file with retry logic.

        Args:
            url: The URL to download from.
            dest_path: Destination path for the downloaded file.
            artifact_key: Artifact key for error messages.

        Raises:
            PolicyDownloadError: If download fails after all retries.
        """
        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.get(url, follow_redirects=True)
                    response.raise_for_status()

                    # Write to temp file first
                    temp_path = dest_path.with_suffix(".tmp")
                    temp_path.write_bytes(response.content)

                    # Atomic rename
                    temp_path.rename(dest_path)
                    return

            except httpx.HTTPStatusError as e:
                last_error = e
                # Don't retry on 4xx errors except 429
                if 400 <= e.response.status_code < 500:
                    if e.response.status_code != 429:
                        raise PolicyDownloadError(
                            artifact_key,
                            f"HTTP {e.response.status_code}: {e.response.text}",
                        )

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = e

            # Exponential backoff
            if attempt < self.max_retries - 1:
                wait_time = (2**attempt) * 0.5
                time.sleep(wait_time)

        raise PolicyDownloadError(
            artifact_key,
            f"Failed after {self.max_retries} attempts: {last_error}",
        )

    def download_artifact(
        self,
        artifact: PolicyArtifact,
        force: bool = False,
    ) -> tuple[Path, str]:
        """Download a single policy artifact.

        Args:
            artifact: The policy artifact to download.
            force: Force download even if cached.

        Returns:
            Tuple of (local_path, verified_sha256).

        Raises:
            PolicyDownloadError: If download fails.
            PolicyIntegrityError: If SHA256 verification fails.
        """
        if not artifact.artifact_uri:
            raise PolicyDownloadError(artifact.key, "No artifact URI provided")

        cache_path = self._get_cache_path(artifact)

        # Check cache first
        if not force and self.is_cached(artifact):
            actual_sha256 = self._compute_sha256(cache_path)
            return cache_path, actual_sha256

        # Create cache directory
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Download the artifact
        self._download_with_retry(
            url=artifact.artifact_uri,
            dest_path=cache_path,
            artifact_key=artifact.key,
        )

        # Verify SHA256
        actual_sha256 = self._compute_sha256(cache_path)
        if artifact.artifact_sha256 and actual_sha256 != artifact.artifact_sha256:
            # Remove the corrupted file
            cache_path.unlink()
            raise PolicyIntegrityError(
                artifact_key=artifact.key,
                expected=artifact.artifact_sha256,
                actual=actual_sha256,
            )

        return cache_path, actual_sha256

    def download_artifacts(
        self,
        artifacts: list[PolicyArtifact],
        force: bool = False,
    ) -> dict[str, tuple[Path, str]]:
        """Download multiple policy artifacts.

        Args:
            artifacts: List of policy artifacts to download.
            force: Force download even if cached.

        Returns:
            Dict mapping artifact key to (local_path, verified_sha256).

        Raises:
            PolicyDownloadError: If any download fails.
            PolicyIntegrityError: If any SHA256 verification fails.
        """
        results: dict[str, tuple[Path, str]] = {}

        for artifact in artifacts:
            if not artifact.artifact_uri:
                continue

            path, sha256 = self.download_artifact(artifact, force=force)
            results[artifact.key] = (path, sha256)

        return results

    def download_and_save(
        self,
        run_state: ScanRunState,
        artifacts: list[PolicyArtifact],
        force: bool = False,
    ) -> dict[str, tuple[Path, str]]:
        """Download artifacts and update run state.

        Args:
            run_state: The current scan run state.
            artifacts: List of policy artifacts to download.
            force: Force download even if cached.

        Returns:
            Dict mapping artifact key to (local_path, verified_sha256).
        """
        run_state.start_phase("download_artifacts")

        try:
            results = self.download_artifacts(artifacts, force=force)

            run_state.complete_phase(
                "download_artifacts",
                artifacts_downloaded=len(results),
                cache_hits=sum(1 for a in artifacts if self.is_cached(a)),
            )

            return results

        except Exception as e:
            run_state.fail_phase("download_artifacts", str(e))
            raise

    def get_artifact_paths(
        self,
        downloaded: dict[str, tuple[Path, str]],
    ) -> list[Path]:
        """Get list of downloaded artifact paths.

        Args:
            downloaded: Result from download_artifacts().

        Returns:
            List of local paths to downloaded artifacts.
        """
        return [path for path, _ in downloaded.values()]

    def get_artifact_sha256s(
        self,
        downloaded: dict[str, tuple[Path, str]],
    ) -> dict[str, str]:
        """Get mapping of artifact key to verified SHA256.

        Args:
            downloaded: Result from download_artifacts().

        Returns:
            Dict mapping artifact key to SHA256 hash.
        """
        return {key: sha256 for key, (_, sha256) in downloaded.items()}
