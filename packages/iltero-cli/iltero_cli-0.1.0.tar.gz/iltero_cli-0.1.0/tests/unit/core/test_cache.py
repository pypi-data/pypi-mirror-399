"""Tests for PolicyCache."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from iltero.core.cache import PolicyCache


class TestPolicyCache:
    """Tests for PolicyCache class."""

    @pytest.fixture
    def cache_dir(self, tmp_path: Path) -> Path:
        """Create a temporary cache directory."""
        cache_path = tmp_path / "policies"
        cache_path.mkdir()
        return cache_path

    @pytest.fixture
    def cache(self, cache_dir: Path) -> PolicyCache:
        """Create a PolicyCache instance with temp directory."""
        return PolicyCache(cache_dir=cache_dir, max_age_hours=24)

    @pytest.fixture
    def sample_policy(self) -> dict:
        """Sample policy data for testing."""
        return {
            "id": "cis-aws-1.4",
            "name": "CIS AWS Foundations 1.4",
            "rules": [
                {"id": "rule-1", "check": "ensure_s3_encryption"},
                {"id": "rule-2", "check": "ensure_iam_mfa"},
            ],
        }

    def test_init_creates_cache_dir(self, tmp_path: Path) -> None:
        """Test that cache directory is created on init."""
        cache_dir = tmp_path / "new_cache_dir"
        assert not cache_dir.exists()

        PolicyCache(cache_dir=cache_dir)

        assert cache_dir.exists()

    def test_set_and_get(self, cache: PolicyCache, sample_policy: dict) -> None:
        """Test caching and retrieving a policy bundle."""
        policy_id = "test-policy"

        # Cache the policy
        cache_path = cache.set(policy_id, sample_policy)

        assert cache_path.exists()

        # Retrieve the policy
        cached = cache.get(policy_id)

        assert cached == sample_policy

    def test_get_returns_none_for_missing(self, cache: PolicyCache) -> None:
        """Test that get returns None for non-existent policy."""
        result = cache.get("non-existent")

        assert result is None

    def test_get_returns_none_for_stale_cache(self, cache_dir: Path, sample_policy: dict) -> None:
        """Test that stale cache entries are invalidated."""
        # Create cache with very short max age
        cache = PolicyCache(cache_dir=cache_dir, max_age_hours=0)
        policy_id = "stale-policy"

        # Cache the policy
        cache.set(policy_id, sample_policy)

        # Manually make the cache stale by modifying metadata
        meta_path = cache._get_metadata_path(policy_id)
        with open(meta_path) as f:
            metadata = json.load(f)

        # Set cached_at to 25 hours ago
        old_time = datetime.now() - timedelta(hours=25)
        metadata["cached_at"] = old_time.isoformat()

        with open(meta_path, "w") as f:
            json.dump(metadata, f)

        # Cache with 24 hour max age
        cache = PolicyCache(cache_dir=cache_dir, max_age_hours=24)

        # Should return None and invalidate
        result = cache.get(policy_id)

        assert result is None

    def test_invalidate(self, cache: PolicyCache, sample_policy: dict) -> None:
        """Test invalidating a cache entry."""
        policy_id = "to-invalidate"

        cache.set(policy_id, sample_policy)
        assert cache.get(policy_id) is not None

        # Invalidate
        result = cache.invalidate(policy_id)

        assert result is True
        assert cache.get(policy_id) is None

    def test_invalidate_returns_false_for_missing(self, cache: PolicyCache) -> None:
        """Test invalidating non-existent entry returns False."""
        result = cache.invalidate("non-existent")

        assert result is False

    def test_clear(self, cache: PolicyCache, sample_policy: dict) -> None:
        """Test clearing all cache entries."""
        # Cache multiple policies
        cache.set("policy-1", sample_policy)
        cache.set("policy-2", sample_policy)
        cache.set("policy-3", sample_policy)

        # Clear all
        count = cache.clear()

        # Should have cleared 6 files (3 policies + 3 metadata)
        assert count == 6
        assert cache.get("policy-1") is None
        assert cache.get("policy-2") is None
        assert cache.get("policy-3") is None

    def test_cleanup_stale(self, cache_dir: Path, sample_policy: dict) -> None:
        """Test cleanup of stale entries only."""
        cache = PolicyCache(cache_dir=cache_dir, max_age_hours=24)

        # Cache a fresh policy
        cache.set("fresh-policy", sample_policy)

        # Cache a stale policy with old timestamp
        cache.set("stale-policy", sample_policy)
        meta_path = cache._get_metadata_path("stale-policy")
        with open(meta_path) as f:
            metadata = json.load(f)

        old_time = datetime.now() - timedelta(hours=48)
        metadata["cached_at"] = old_time.isoformat()
        with open(meta_path, "w") as f:
            json.dump(metadata, f)

        # Cleanup stale entries
        count = cache.cleanup_stale()

        assert count == 1
        assert cache.get("fresh-policy") == sample_policy
        assert cache.get("stale-policy") is None

    def test_get_cache_info(self, cache: PolicyCache, sample_policy: dict) -> None:
        """Test getting cache information."""
        cache.set("policy-1", sample_policy)
        cache.set("policy-2", sample_policy)

        info = cache.get_cache_info()

        assert info["total_entries"] == 2
        assert info["total_size_bytes"] > 0
        assert info["max_age_hours"] == 24
        assert len(info["entries"]) == 2

    def test_has_valid_cache_with_matching_hash(
        self, cache: PolicyCache, sample_policy: dict
    ) -> None:
        """Test hash validation for cache entries."""
        policy_id = "hash-test"

        # Cache with computed hash
        cache.set(policy_id, sample_policy)

        # Compute expected hash
        expected_hash = cache._compute_hash(sample_policy)

        assert cache.has_valid_cache(policy_id, expected_hash) is True
        assert cache.has_valid_cache(policy_id, "wrong-hash") is False

    def test_has_valid_cache_returns_false_for_stale(
        self, cache_dir: Path, sample_policy: dict
    ) -> None:
        """Test that has_valid_cache returns False for stale entries."""
        cache = PolicyCache(cache_dir=cache_dir, max_age_hours=24)
        policy_id = "stale-hash-test"

        cache.set(policy_id, sample_policy)
        expected_hash = cache._compute_hash(sample_policy)

        # Make cache stale
        meta_path = cache._get_metadata_path(policy_id)
        with open(meta_path) as f:
            metadata = json.load(f)

        old_time = datetime.now() - timedelta(hours=48)
        metadata["cached_at"] = old_time.isoformat()
        with open(meta_path, "w") as f:
            json.dump(metadata, f)

        assert cache.has_valid_cache(policy_id, expected_hash) is False

    def test_policy_id_with_slashes(self, cache: PolicyCache, sample_policy: dict) -> None:
        """Test that policy IDs with slashes are handled correctly."""
        policy_id = "org/team/policy-name"

        cache.set(policy_id, sample_policy)
        cached = cache.get(policy_id)

        assert cached == sample_policy

    def test_corrupt_cache_file_handled(self, cache: PolicyCache) -> None:
        """Test that corrupt cache files are handled gracefully."""
        policy_id = "corrupt-policy"

        # Create a corrupt cache file
        cache_path = cache._get_cache_path(policy_id)
        cache_path.write_text("not valid json {{{")

        # Create valid metadata
        meta_path = cache._get_metadata_path(policy_id)
        meta_path.write_text(
            json.dumps(
                {
                    "policy_set_id": policy_id,
                    "cached_at": datetime.now().isoformat(),
                    "content_hash": "abc123",
                    "max_age_hours": 24,
                }
            )
        )

        # Should return None and invalidate
        result = cache.get(policy_id)

        assert result is None
        assert not cache_path.exists()

    def test_corrupt_metadata_handled(self, cache: PolicyCache, sample_policy: dict) -> None:
        """Test that corrupt metadata files are handled gracefully."""
        policy_id = "corrupt-meta"

        # Set up valid cache
        cache.set(policy_id, sample_policy)

        # Corrupt the metadata
        meta_path = cache._get_metadata_path(policy_id)
        meta_path.write_text("not valid json")

        # Should treat as stale
        assert cache._is_stale(policy_id) is True
