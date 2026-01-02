"""Memory estimation utilities for large dataset handling."""

from dataclasses import dataclass
from typing import Any


@dataclass
class MemoryEstimate:
    """Memory usage estimate for large dataset handling."""
    estimated_bytes: int
    estimated_mb: float
    requires_warning: bool = False
    requires_confirmation: bool = False

    @classmethod
    def calculate(cls, input_length: int, data_structure: Any) -> "MemoryEstimate":
        """
        Calculate memory usage estimate for input data.

        Args:
            input_length: Length of input string in characters
            data_structure: Parsed Python data structure

        Returns:
            MemoryEstimate with usage estimates and flags
        """
        # Formula: input_length * 3 (UTF-8) * 1.5 (Python overhead)
        estimated_bytes = int(input_length * 3 * 1.5)

        # Add structure overhead
        if isinstance(data_structure, dict):
            estimated_bytes += len(data_structure) * 100  # Per-key overhead
        elif isinstance(data_structure, list):
            estimated_bytes += len(data_structure) * 50   # Per-item overhead

        estimated_mb = round(estimated_bytes / (1024 * 1024), 2)

        from ..config.constants import (
            MEMORY_WARNING_THRESHOLD_MB,
            MEMORY_CONFIRMATION_THRESHOLD_MB
        )

        return cls(
            estimated_bytes=estimated_bytes,
            estimated_mb=estimated_mb,
            requires_warning=estimated_mb > MEMORY_WARNING_THRESHOLD_MB,
            requires_confirmation=estimated_mb > MEMORY_CONFIRMATION_THRESHOLD_MB
        )
