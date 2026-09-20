"""Read-only storage-provider contract for discovery."""

# standard imports
from pathlib import Path
from typing import Protocol

# 1st-party imports
from ryujinx_save_manager.core.models import DiscoveryReport


class StorageProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    def discover(self, root: Path) -> DiscoveryReport:
        """Return normalized saves and diagnostics without modifying the source tree."""
        ...
