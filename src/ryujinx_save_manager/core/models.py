"""Format-neutral save identity and discovery models."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DiscoveredSave:
    """A save container identified by a storage provider, not parsed game data."""

    provider_id: str
    container_path: Path
    title_id: str | None = None
    user_id: str | None = None
    display_name: str | None = None
