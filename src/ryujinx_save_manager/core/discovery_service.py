"""Application boundary for read-only save discovery."""

# standard imports
from dataclasses import dataclass
from pathlib import Path

# 1st-party imports
from ryujinx_save_manager.core.models import DiscoveryReport
from ryujinx_save_manager.storage.storage_provider import StorageProvider


@dataclass(frozen=True, slots=True)
class DiscoveryService:
    provider: StorageProvider

    def scan(self, root: Path) -> DiscoveryReport:
        """Discover saves under the caller-selected directory without writes."""
        return self.provider.discover(root)
