"""Game plugin boundary. This API will evolve before write support is enabled."""

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from ryujinx_save_manager.core.models import DiscoveredSave


class GamePlugin(Protocol):
    @property
    def plugin_id(self) -> str: ...

    @property
    def display_name(self) -> str: ...

    @property
    def title_ids(self) -> frozenset[str]: ...

    def detects(self, save: DiscoveredSave) -> bool:
        """Read-only detection; never mutate the save container."""
        ...

    def relevant_files(self, save: DiscoveredSave) -> Sequence[Path]:
        """Relative paths needed for a complete backup; include metadata files."""
        ...
