"""
Asset model (sketch) — a plain dataclass with zero external dependencies.

Lives in `core/` so every layer (Maya, standalone, future web/service) shares the
exact same notion of an asset. No Qt, no maya, no sqlite here — just data.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple


# Allowed statuses kept as a simple tuple constant rather than an enum to stay
# trivially serializable to JSON / sqlite / a future REST payload.
STATUSES = ("wip", "review", "approved")


@dataclass
class Asset:
    """A single tracked asset.

    `id` is assigned by the repository on insert (None until persisted), so the
    same dataclass represents both an in-memory draft and a stored row.
    """

    name: str
    asset_type: str                      # "character" | "prop" | "environment" | ...
    path: str = ""                       # published/source file location
    version: int = 1
    status: str = "wip"                  # one of STATUSES
    tags: Tuple[str, ...] = field(default_factory=tuple)
    id: Optional[int] = None

    def with_id(self, new_id: int) -> "Asset":
        """Return a copy stamped with the given primary key (post-insert)."""
        return Asset(
            name=self.name,
            asset_type=self.asset_type,
            path=self.path,
            version=self.version,
            status=self.status,
            tags=tuple(self.tags),
            id=new_id,
        )
