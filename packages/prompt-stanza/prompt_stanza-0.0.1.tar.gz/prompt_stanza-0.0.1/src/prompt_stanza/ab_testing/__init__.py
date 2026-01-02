"""A/B testing module for prompt version selection."""

import random
from dataclasses import dataclass

from ..exceptions import ValidationError
from ..input_adapters.base import BaseInputAdapter
from ..models import PromptConfig
from .multi_variant import MultiVariantSelector, VariantConfig


@dataclass
class ABTestConfig:
    """Configuration for A/B test between two prompt versions."""

    version_a: str
    version_b: str
    probability_a: float = 0.5

    def __post_init__(self):
        """Validate A/B test configuration."""
        if not 0.0 <= self.probability_a <= 1.0:
            raise ValidationError(
                f"probability_a must be between 0.0 and 1.0, got: {self.probability_a}"
            )
        if self.version_a == self.version_b:
            raise ValidationError(
                f"version_a and version_b must be different, got: {self.version_a}"
            )

    @property
    def probability_b(self) -> float:
        """Calculate probability for version B."""
        return 1.0 - self.probability_a


class ABTestSelector:
    """
    A/B test selector for choosing between two prompt versions.

    Features:
    - Probabilistic selection between two versions
    - Session-based consistency (same user gets same version)
    - Weighted distribution support
    - Selection tracking and analytics

    Examples:
        # Create selector with 70/30 split
        selector = ABTestSelector(
            adapter=adapter,
            ab_config=ABTestConfig(
                version_a="1.0.0",
                version_b="2.0.0",
                probability_a=0.7
            )
        )

        # Load prompt - randomly selects version based on probability
        config = selector.load("code_review")

        # Load with session consistency (same session_id always gets same version)
        config = selector.load("code_review", session_id="user123")

        # Get selection statistics
        stats = selector.get_statistics()
    """

    def __init__(
        self,
        adapter: BaseInputAdapter,
        ab_config: ABTestConfig,
        seed: int | None = None,
    ):
        """
        Initialize A/B test selector.

        Args:
            adapter: Input adapter for loading prompts
            ab_config: A/B test configuration
            seed: Random seed for reproducible testing (None for random)
        """
        self.adapter = adapter
        self.ab_config = ab_config
        self._random = random.Random(seed)

        # Track selections for analytics
        self._selections_a = 0
        self._selections_b = 0
        self._session_cache: dict[str, str] = {}

    def _select_version(self, session_id: str | None = None) -> str:
        """
        Select a version based on probability or session cache.

        Args:
            session_id: Optional session identifier for consistent selection

        Returns:
            Selected version string (version_a or version_b)
        """
        # Check session cache for consistency
        if session_id is not None and session_id in self._session_cache:
            return self._session_cache[session_id]

        # Probabilistic selection
        rand_val = self._random.random()
        selected_version = (
            self.ab_config.version_a
            if rand_val < self.ab_config.probability_a
            else self.ab_config.version_b
        )

        # Update statistics
        if selected_version == self.ab_config.version_a:
            self._selections_a += 1
        else:
            self._selections_b += 1

        # Cache for session consistency
        if session_id is not None:
            self._session_cache[session_id] = selected_version

        return selected_version

    def load(
        self,
        identifier: str,
        session_id: str | None = None,
        force_version: str | None = None,
    ) -> PromptConfig:
        """
        Load a prompt with A/B test version selection.

        Args:
            identifier: Prompt identifier
            session_id: Optional session ID for consistent version selection
            force_version: Force a specific version (bypass A/B test)

        Returns:
            PromptConfig for the selected version

        Raises:
            StanzaNotFoundError: If prompt cannot be found
            AdapterError: If loading fails
        """
        version = force_version if force_version is not None else self._select_version(session_id)

        return self.adapter.load(identifier, version)

    def get_selected_version(self, session_id: str | None = None) -> str:
        """
        Get the version that would be selected (without loading).

        Args:
            session_id: Optional session ID

        Returns:
            Version string that would be selected
        """
        return self._select_version(session_id)

    def get_statistics(self) -> dict:
        """
        Get A/B test selection statistics.

        Returns:
            Dictionary with selection counts and percentages
        """
        total = self._selections_a + self._selections_b

        if total == 0:
            return {
                "version_a": self.ab_config.version_a,
                "version_b": self.ab_config.version_b,
                "selections_a": 0,
                "selections_b": 0,
                "percentage_a": 0.0,
                "percentage_b": 0.0,
                "total_selections": 0,
                "expected_probability_a": self.ab_config.probability_a,
                "expected_probability_b": self.ab_config.probability_b,
            }

        return {
            "version_a": self.ab_config.version_a,
            "version_b": self.ab_config.version_b,
            "selections_a": self._selections_a,
            "selections_b": self._selections_b,
            "percentage_a": (self._selections_a / total) * 100,
            "percentage_b": (self._selections_b / total) * 100,
            "total_selections": total,
            "expected_probability_a": self.ab_config.probability_a,
            "expected_probability_b": self.ab_config.probability_b,
            "session_cache_size": len(self._session_cache),
        }

    def reset_statistics(self) -> None:
        """Reset selection statistics."""
        self._selections_a = 0
        self._selections_b = 0

    def clear_session_cache(self) -> None:
        """Clear session cache."""
        self._session_cache.clear()

    def reset(self) -> None:
        """Reset both statistics and session cache."""
        self.reset_statistics()
        self.clear_session_cache()


__all__ = [
    "ABTestConfig",
    "ABTestSelector",
    "MultiVariantSelector",
    "VariantConfig",
]
