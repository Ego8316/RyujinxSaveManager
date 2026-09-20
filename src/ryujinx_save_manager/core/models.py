"""Format-neutral save identity and discovery models."""

# standard imports
from dataclasses import dataclass
from pathlib import Path

# 1st-party imports
from ryujinx_save_manager.core.discovery_diagnostic_code import DiscoveryDiagnosticCode


@dataclass(frozen=True, slots=True)
class DiscoveredSave:
    """A save container identified by a storage provider, not parsed game data."""

    provider_id: str
    container_path: Path
    title_id: str | None = None
    user_id: str | None = None
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class DiscoveryDiagnostic:
    """A recoverable discovery concern with stable text and optional context."""

    code: DiscoveryDiagnosticCode
    path: Path
    detail: str | None = None

    @property
    def message(self) -> str:
        if self.detail:
            return f"{self.code.message}: {self.detail}"
        return self.code.message


@dataclass(frozen=True, slots=True)
class DiscoveryReport:
    saves: tuple[DiscoveredSave, ...]
    diagnostics: tuple[DiscoveryDiagnostic, ...]
