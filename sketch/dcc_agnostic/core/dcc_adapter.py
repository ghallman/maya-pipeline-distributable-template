"""
DccAdapter (sketch) — the single seam between shared UI/logic and a concrete host.

The shared asset-manager widget talks ONLY to this interface, never to `maya.*`.
Each host provides one implementation:
  - dcc/maya/adapter.py       -> MayaDccAdapter
  - dcc/standalone/adapter.py -> StandaloneDccAdapter

This is what lets one GUI mirror across Maya and standalone: swap the adapter.
Lives in `core/` and imports nothing host- or Qt-specific.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from core.assetmanager.models import Asset


class DccAdapter(ABC):
    """Host capabilities the asset manager needs, abstracted away from any DCC."""

    #: Human-readable host name, e.g. "Maya 2026" or "Standalone".
    host_name: str = "unknown"

    @abstractmethod
    def get_main_window(self) -> Optional[Any]:
        """Return the parent window for dialogs (QWidget), or None when headless.

        Maya: the wrapped Maya main window. Standalone: the app's top-level window.
        """

    @abstractmethod
    def open_file(self, path: str) -> None:
        """Open a file in the host (Maya: load scene; Standalone: OS default app)."""

    @abstractmethod
    def import_asset(self, asset: Asset) -> None:
        """Bring an asset into the current context.

        Maya: reference/import the asset's file. Standalone: no scene exists, so
        this is a no-op or an OS-level reveal/copy — that divergence is exactly
        why it lives behind the adapter.
        """

    @abstractmethod
    def export_selection(self, path: str) -> None:
        """Publish the current selection/scene to `path` (Maya only in practice)."""

    @abstractmethod
    def current_scene(self) -> Optional[str]:
        """Path of the open scene, or None when there is no DCC scene."""
