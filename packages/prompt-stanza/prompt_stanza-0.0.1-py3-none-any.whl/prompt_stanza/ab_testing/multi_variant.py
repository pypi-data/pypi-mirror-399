"""Multi-variant testing module for testing more than 2 versions."""

import random
from dataclasses import dataclass

from ..exceptions import ValidationError
from ..input_adapters.base import BaseInputAdapter
from ..models import PromptConfig


@dataclass
class VariantConfig:
    """Configuration for a single variant in multi-variant test."""

    version: str
    weight: float = 1.0

    def __post_init__(self):
        """Validate variant configuration."""
        if self.weight < 0:
            raise ValidationError(f"weight must be non-negative, got: {self.weight}")


class MultiVariantSelector:
    """
    Multi-variant test selector for choosing between multiple prompt versions.

    Supports A/B/C/D/... testing with weighted distribution.

    Features:
    - Support for 2+ variants with weighted distribution
    - Session-based consistency
    - Selection tracking and analytics
    - Automatic weight normalization

    Examples:
        # Create selector with 3 variants (50/30/20 split)
        selector = MultiVariantSelector(
            adapter=adapter,
            variants=[
                VariantConfig(version="1.0.0", weight=0.5),
                VariantConfig(version="2.0.0", weight=0.3),
                VariantConfig(version="3.0.0", weight=0.2),
            ]
        )

        # Load prompt - randomly selects version based on weights
        config = selector.load("code_review")

        # Load with session consistency
        config = selector.load("code_review", session_id="user123")

        # Get selection statistics
        stats = selector.get_statistics()
    """

    def __init__(
        self,
        adapter: BaseInputAdapter,
        variants: list[VariantConfig],
        seed: int | None = None,
    ):
        """
        Initialize multi-variant test selector.

        Args:
            adapter: Input adapter for loading prompts
            variants: List of variant configurations (minimum 2)
            seed: Random seed for reproducible testing (None for random)

        Raises:
            ValidationError: If less than 2 variants provided
        """
        if len(variants) < 2:
            raise ValidationError(f"At least 2 variants required for testing, got: {len(variants)}")

        self.adapter = adapter
        self.variants = variants
        self._random = random.Random(seed)

        # Normalize weights to probabilities
        total_weight = sum(v.weight for v in variants)
        if total_weight == 0:
            raise ValidationError("Total weight of all variants must be greater than 0")

        self._probabilities = [v.weight / total_weight for v in variants]
        self._cumulative_probs = []
        cumsum = 0.0
        for prob in self._probabilities:
            cumsum += prob
            self._cumulative_probs.append(cumsum)

        # Track selections for analytics
        self._selections: dict[str, int] = {v.version: 0 for v in variants}
        self._session_cache: dict[str, str] = {}

    def _select_version(self, session_id: str | None = None) -> str:
        """
        Select a version based on weighted probabilities or session cache.

        Args:
            session_id: Optional session identifier for consistent selection

        Returns:
            Selected version string
        """
        # Check session cache for consistency
        if session_id is not None and session_id in self._session_cache:
            return self._session_cache[session_id]

        # Weighted random selection
        rand_val = self._random.random()
        selected_idx = 0
        for idx, cumprob in enumerate(self._cumulative_probs):
            if rand_val < cumprob:
                selected_idx = idx
                break

        selected_version = self.variants[selected_idx].version

        # Update statistics
        self._selections[selected_version] += 1

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
        Load a prompt with multi-variant version selection.

        Args:
            identifier: Prompt identifier
            session_id: Optional session ID for consistent version selection
            force_version: Force a specific version (bypass testing)

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
        Get multi-variant test selection statistics.

        Returns:
            Dictionary with selection counts and percentages per variant
        """
        total = sum(self._selections.values())

        variant_stats = []
        for idx, variant in enumerate(self.variants):
            selections = self._selections[variant.version]
            percentage = (selections / total * 100) if total > 0 else 0.0

            variant_stats.append(
                {
                    "version": variant.version,
                    "weight": variant.weight,
                    "expected_probability": self._probabilities[idx],
                    "selections": selections,
                    "percentage": percentage,
                }
            )

        return {
            "variants": variant_stats,
            "total_selections": total,
            "session_cache_size": len(self._session_cache),
        }

    def reset_statistics(self) -> None:
        """Reset selection statistics."""
        for version in self._selections:
            self._selections[version] = 0

    def clear_session_cache(self) -> None:
        """Clear session cache."""
        self._session_cache.clear()

    def reset(self) -> None:
        """Reset both statistics and session cache."""
        self.reset_statistics()
        self.clear_session_cache()
