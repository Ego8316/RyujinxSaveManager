"""Read-only storage-provider contract for discovery."""

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from ryujinx_save_manager.core.models import DiscoveredSave


class StorageProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    def discover(self, root: Path) -> Sequence[DiscoveredSave]:
        """Return normalized saves without modifying the source tree."""
        ...
