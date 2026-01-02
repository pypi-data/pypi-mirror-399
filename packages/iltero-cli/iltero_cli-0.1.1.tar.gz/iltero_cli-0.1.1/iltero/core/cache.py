"""Policy bundle caching for improved performance."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default cache configuration
DEFAULT_CACHE_DIR = Path.home() / ".iltero" / "policies"
DEFAULT_MAX_AGE_HOURS = 24


class PolicyCache:
    """Cache policy bundles locally to reduce API calls.

    The cache stores policy bundles as JSON files in a configurable directory,
    with automatic staleness checking and cleanup.

    Attributes:
        cache_dir: Directory where cached bundles are stored.
        max_age_hours: Max age in hours before a cached bundle is stale.

    Example:
        >>> cache = PolicyCache()
        >>> cache.set("my-policy-set", {"rules": [...]})
        >>> bundle = cache.get("my-policy-set")
        >>> if bundle is None:
        ...     # Fetch from API and cache
        ...     bundle = api.fetch_policy_set("my-policy-set")
        ...     cache.set("my-policy-set", bundle)
    """

    def __init__(
        self,
        cache_dir: Path | None = None,
        max_age_hours: int = DEFAULT_MAX_AGE_HOURS,
    ) -> None:
        """Initialize the policy cache.

        Args:
            cache_dir: Directory for cached policy bundles.
                       Defaults to ~/.iltero/policies
            max_age_hours: Max age in hours before cache is stale.
                           Defaults to 24.
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.max_age_hours = max_age_hours
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, policy_set_id: str) -> Path:
        """Get the cache file path for a policy set.

        Args:
            policy_set_id: Unique identifier for the policy set.

        Returns:
            Path to the cache file.
        """
        # Sanitize policy set ID for use as filename
        safe_id = policy_set_id.replace("/", "_").replace("\\", "_")
        return self.cache_dir / f"{safe_id}.json"

    def _get_metadata_path(self, policy_set_id: str) -> Path:
        """Get the metadata file path for a policy set.

        Args:
            policy_set_id: Unique identifier for the policy set.

        Returns:
            Path to the metadata file.
        """
        safe_id = policy_set_id.replace("/", "_").replace("\\", "_")
        return self.cache_dir / f"{safe_id}.meta.json"

    def _is_stale(self, policy_set_id: str) -> bool:
        """Check if a cached policy bundle is stale.

        Args:
            policy_set_id: Unique identifier for the policy set.

        Returns:
            True if the cache is stale or doesn't exist, False otherwise.
        """
        metadata_path = self._get_metadata_path(policy_set_id)

        if not metadata_path.exists():
            return True

        try:
            with open(metadata_path) as f:
                metadata = json.load(f)

            cached_at = datetime.fromisoformat(metadata.get("cached_at", ""))
            age = datetime.now() - cached_at
            return age > timedelta(hours=self.max_age_hours)
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Failed to read cache metadata for {policy_set_id}: {e}")
            return True

    def _compute_hash(self, data: dict[str, Any]) -> str:
        """Compute a hash of the policy data for cache invalidation.

        Args:
            data: Policy bundle data.

        Returns:
            SHA256 hash of the serialized data.
        """
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def get(self, policy_set_id: str) -> dict[str, Any] | None:
        """Get a cached policy bundle.

        Returns None if the bundle doesn't exist or is stale.

        Args:
            policy_set_id: Unique identifier for the policy set.

        Returns:
            Cached policy bundle data, or None if not available or stale.
        """
        cache_path = self._get_cache_path(policy_set_id)

        if not cache_path.exists():
            logger.debug(f"Cache miss for policy set: {policy_set_id}")
            return None

        if self._is_stale(policy_set_id):
            logger.debug(f"Cache stale for policy set: {policy_set_id}")
            self.invalidate(policy_set_id)
            return None

        try:
            with open(cache_path) as f:
                data = json.load(f)
            logger.debug(f"Cache hit for policy set: {policy_set_id}")
            return data
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to read cached policy set {policy_set_id}: {e}")
            self.invalidate(policy_set_id)
            return None

    def set(
        self,
        policy_set_id: str,
        data: dict[str, Any],
        content_hash: str | None = None,
    ) -> Path:
        """Cache a policy bundle.

        Args:
            policy_set_id: Unique identifier for the policy set.
            data: Policy bundle data to cache.
            content_hash: Optional hash of the content for validation.

        Returns:
            Path to the cached file.
        """
        cache_path = self._get_cache_path(policy_set_id)
        metadata_path = self._get_metadata_path(policy_set_id)

        # Compute hash if not provided
        if content_hash is None:
            content_hash = self._compute_hash(data)

        # Write policy data
        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2)

        # Write metadata
        metadata = {
            "policy_set_id": policy_set_id,
            "cached_at": datetime.now().isoformat(),
            "content_hash": content_hash,
            "max_age_hours": self.max_age_hours,
        }
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.debug(f"Cached policy set: {policy_set_id}")
        return cache_path

    def invalidate(self, policy_set_id: str) -> bool:
        """Invalidate (remove) a cached policy bundle.

        Args:
            policy_set_id: Unique identifier for the policy set.

        Returns:
            True if the cache was invalidated, False if it didn't exist.
        """
        cache_path = self._get_cache_path(policy_set_id)
        metadata_path = self._get_metadata_path(policy_set_id)

        removed = False

        if cache_path.exists():
            cache_path.unlink()
            removed = True

        if metadata_path.exists():
            metadata_path.unlink()
            removed = True

        if removed:
            logger.debug(f"Invalidated cache for policy set: {policy_set_id}")

        return removed

    def clear(self) -> int:
        """Clear all cached policy bundles.

        Returns:
            Number of cache entries cleared.
        """
        count = 0
        for file_path in self.cache_dir.glob("*.json"):
            file_path.unlink()
            count += 1

        logger.debug(f"Cleared {count} cached policy files")
        return count

    def cleanup_stale(self) -> int:
        """Remove all stale cache entries.

        Returns:
            Number of stale entries removed.
        """
        count = 0
        for meta_file in self.cache_dir.glob("*.meta.json"):
            # Extract policy set ID from metadata filename
            policy_set_id = meta_file.stem.replace(".meta", "")

            if self._is_stale(policy_set_id):
                self.invalidate(policy_set_id)
                count += 1

        if count > 0:
            logger.debug(f"Cleaned up {count} stale cache entries")

        return count

    def get_cache_info(self) -> dict[str, Any]:
        """Get information about the cache.

        Returns:
            Dictionary with cache statistics.
        """
        cache_entries = []
        total_size = 0

        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file.stem.endswith(".meta"):
                continue

            policy_set_id = cache_file.stem
            size = cache_file.stat().st_size
            total_size += size

            metadata_path = self._get_metadata_path(policy_set_id)
            cached_at = None
            is_stale = True

            if metadata_path.exists():
                try:
                    with open(metadata_path) as f:
                        metadata = json.load(f)
                    cached_at = metadata.get("cached_at")
                    is_stale = self._is_stale(policy_set_id)
                except (json.JSONDecodeError, ValueError):
                    pass

            cache_entries.append(
                {
                    "policy_set_id": policy_set_id,
                    "size_bytes": size,
                    "cached_at": cached_at,
                    "is_stale": is_stale,
                }
            )

        return {
            "cache_dir": str(self.cache_dir),
            "max_age_hours": self.max_age_hours,
            "total_entries": len(cache_entries),
            "total_size_bytes": total_size,
            "entries": cache_entries,
        }

    def has_valid_cache(self, policy_set_id: str, content_hash: str) -> bool:
        """Check if a valid (non-stale, matching hash) cache exists.

        Args:
            policy_set_id: Unique identifier for the policy set.
            content_hash: Expected hash of the content.

        Returns:
            True if valid cache exists with matching hash.
        """
        if self._is_stale(policy_set_id):
            return False

        metadata_path = self._get_metadata_path(policy_set_id)
        if not metadata_path.exists():
            return False

        try:
            with open(metadata_path) as f:
                metadata = json.load(f)
            return metadata.get("content_hash") == content_hash
        except (json.JSONDecodeError, ValueError):
            return False
