"""Base input adapter interface for prompt template loading."""

import sys
import time
from abc import ABC, abstractmethod
from collections import OrderedDict

import yaml

from ..models import PromptConfig


class BaseInputAdapter(ABC):
    """
    Abstract base class for input adapters.

    Input adapters are responsible for loading prompt templates from various
    sources (inline strings, YAML files, databases, APIs, etc.).

    Features:
    - Load prompts with version support (semver or "latest")
    - Compile raw content into PromptConfig instances
    - LRU cache with configurable limits (max count or max memory)
    - Optional TTL (time-to-live) for cache entries
    """

    def __init__(
        self,
        cache_enabled: bool = True,
        cache_ttl: int | None = None,
        max_cache_size: int | None = None,
        max_cache_memory_mb: float | None = None,
    ) -> None:
        """
        Initialize the base adapter.

        Args:
            cache_enabled: Whether to enable caching
            cache_ttl: Cache time-to-live in seconds. None means no expiration.
            max_cache_size: Maximum number of items in cache. None means unlimited.
            max_cache_memory_mb: Maximum cache memory in MB. None means unlimited.
        """
        self._cache_enabled = cache_enabled
        self._cache_ttl = cache_ttl
        self._max_cache_size = max_cache_size
        self._max_cache_memory_mb = max_cache_memory_mb
        # Use OrderedDict for LRU behavior
        self._cache: OrderedDict[str, tuple[PromptConfig, float]] = OrderedDict()
        self._cache_memory_bytes = 0

    @abstractmethod
    def load(self, identifier: str, version: str = "latest") -> PromptConfig:
        """
        Load a prompt template from the adapter's source.

        Args:
            identifier: Identifier for the prompt (e.g., name, path, URL)
            version: Version string (semver format like "1.0.0" or "latest")

        Returns:
            PromptConfig instance with validated configuration

        Raises:
            StanzaNotFoundError: If prompt cannot be found
            AdapterError: If loading fails
        """
        pass

    def _compile(self, content: str) -> PromptConfig:
        """
        Compile raw YAML content into a PromptConfig instance.

        This method handles:
        - YAML parsing
        - Schema validation
        - Jinja2 template syntax validation

        Args:
            content: Raw YAML content as string

        Returns:
            Validated PromptConfig instance

        Raises:
            ValueError: If content is invalid
        """
        return PromptConfig.load_yaml(content)

    def _compile_from_dict(self, data: dict) -> PromptConfig:
        """
        Compile dictionary data into a PromptConfig instance.

        Useful for adapters that receive data as dict (JSON, databases).

        Args:
            data: Parsed dictionary data

        Returns:
            Validated PromptConfig instance
        """
        # Convert to YAML string for PromptConfig.load_yaml
        yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        return PromptConfig.load_yaml(yaml_content)

    def _parse_version(self, version_str: str) -> tuple[int, int, int]:
        """
        Parse semantic version string to tuple for comparison.

        Args:
            version_str: Version string (e.g., "1.0.0", "1.0.0.yaml")

        Returns:
            Tuple of (major, minor, patch) as integers

        Raises:
            ValueError: If version string is invalid
        """
        # Remove common file extensions
        version_str = version_str.replace(".yaml", "").replace(".json", "")
        parts = version_str.split(".")
        try:
            return tuple(int(p) for p in parts)  # type: ignore
        except ValueError as e:
            raise ValueError(f"Invalid semantic version: {version_str}") from e

    def _save_to_cache(self, identifier: str, version: str, config: PromptConfig) -> None:
        """
        Save a compiled prompt config to cache (alias for _add_to_cache).

        Args:
            identifier: Prompt identifier
            version: Version string
            config: Compiled PromptConfig instance
        """
        self._add_to_cache(identifier, version, config)

    def _get_cache_key(self, identifier: str, version: str) -> str:
        """
        Generate a cache key for the given identifier and version.

        Args:
            identifier: Prompt identifier
            version: Version string

        Returns:
            Cache key string
        """
        return f"{identifier}:{version}"

    def _get_size_bytes(self, config: PromptConfig) -> int:
        """
        Estimate the memory size of a PromptConfig object in bytes.

        Args:
            config: PromptConfig instance

        Returns:
            Approximate size in bytes
        """
        return sys.getsizeof(config) + sys.getsizeof(config.model_dump_json())

    def _evict_lru(self) -> None:
        """Evict the least recently used item from cache."""
        if self._cache:
            # Remove oldest item (first in OrderedDict)
            oldest_key, (oldest_config, _) = self._cache.popitem(last=False)
            size = self._get_size_bytes(oldest_config)
            self._cache_memory_bytes -= size

    def _add_to_cache(self, identifier: str, version: str, config: PromptConfig) -> None:
        """
        Add a compiled prompt config to cache with LRU eviction.

        Args:
            identifier: Prompt identifier
            version: Version string
            config: Compiled PromptConfig instance
        """
        if not self._cache_enabled:
            return

        cache_key = self._get_cache_key(identifier, version)
        config_size = self._get_size_bytes(config)

        # If item already exists, remove it first to update position
        if cache_key in self._cache:
            old_config, _ = self._cache.pop(cache_key)
            old_size = self._get_size_bytes(old_config)
            self._cache_memory_bytes -= old_size

        # Evict based on max_cache_size (count limit)
        if self._max_cache_size is not None:
            while len(self._cache) >= self._max_cache_size:
                self._evict_lru()

        # Evict based on max_cache_memory_mb (memory limit)
        if self._max_cache_memory_mb is not None:
            max_bytes = self._max_cache_memory_mb * 1024 * 1024
            while self._cache and (self._cache_memory_bytes + config_size) > max_bytes:
                self._evict_lru()

        # Add new item (most recently used goes to end)
        self._cache[cache_key] = (config, time.time())
        self._cache_memory_bytes += config_size

    def _load_from_cache(self, identifier: str, version: str) -> PromptConfig | None:
        """
        Load a prompt config from cache if available and not expired.
        Updates LRU order by moving accessed item to end.

        Args:
            identifier: Prompt identifier
            version: Version string

        Returns:
            Cached PromptConfig instance or None if not in cache or expired
        """
        if not self._cache_enabled:
            return None

        cache_key = self._get_cache_key(identifier, version)
        cached = self._cache.get(cache_key)

        if cached is None:
            return None

        config, timestamp = cached

        # Check if cache entry has expired
        if self._cache_ttl is not None and time.time() - timestamp > self._cache_ttl:
            # Remove expired entry
            size = self._get_size_bytes(config)
            del self._cache[cache_key]
            self._cache_memory_bytes -= size
            return None

        # Move to end (most recently used) for LRU
        self._cache.move_to_end(cache_key)

        return config

    def reset_cache(self) -> None:
        """Clear all cached prompt configurations."""
        self._cache.clear()
        self._cache_memory_bytes = 0
