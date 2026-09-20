"""Conservative, read-only discovery of Ryujinx user-save containers."""

# standard imports
import re
from pathlib import Path

# 1st-party imports
from ryujinx_save_manager.core.discovery_diagnostic_code import DiscoveryDiagnosticCode
from ryujinx_save_manager.core.models import (
    DiscoveredSave,
    DiscoveryDiagnostic,
    DiscoveryReport,
)

_CONTAINER_ID = re.compile(r"[0-9a-fA-F]{16}\Z")
_BANK_NAMES = ("0", "1")
_METADATA_NAMES = ("ExtraData0", "ExtraData1")


class RyujinxStorageProvider:
    """Scan a selected `bis/user/save` directory one level deep.

    Folder names are emulator SaveDataIds, never presumed game Title IDs.
    Historical Ryujinx uses `0` for committed data and `1` for working data;
    discovery checks only their presence. Metadata is likewise checked for
    presence but not parsed until its serialization is fixture-verified.
    """

    @property
    def provider_id(self) -> str:
        return "ryujinx"

    def discover(self, root: Path) -> DiscoveryReport:
        if not root.is_dir():
            raise ValueError(f"Not a readable directory: {root}")

        saves: list[DiscoveredSave] = []
        diagnostics: list[DiscoveryDiagnostic] = []
        for entry in sorted(root.iterdir(), key=lambda path: (path.name.casefold(), path.name)):
            try:
                if entry.is_symlink():
                    diagnostics.append(
                        DiscoveryDiagnostic(DiscoveryDiagnosticCode.SYMLINK_SKIPPED, entry)
                    )
                    continue
                if not entry.is_dir():
                    continue
                bank_names = self._get_bank_names(entry, diagnostics)
                metadata_names = self._get_metadata_names(entry, diagnostics)
                for child in entry.iterdir():
                    if (
                        child.name not in _BANK_NAMES
                        and child.name not in _METADATA_NAMES
                        and child.is_symlink()
                    ):
                        diagnostics.append(
                            DiscoveryDiagnostic(DiscoveryDiagnosticCode.SYMLINK_SKIPPED, child)
                        )
            except OSError as exc:
                diagnostics.append(
                    DiscoveryDiagnostic(DiscoveryDiagnosticCode.UNREADABLE, entry, detail=str(exc))
                )
                continue

            canonical_id = bool(_CONTAINER_ID.fullmatch(entry.name))
            if not bank_names and not metadata_names:
                diagnostics.append(
                    DiscoveryDiagnostic(
                        DiscoveryDiagnosticCode.UNRECOGNIZED_CONTAINER,
                        entry,
                    )
                )
                if not canonical_id:
                    continue
            if not canonical_id:
                diagnostics.append(
                    DiscoveryDiagnostic(
                        DiscoveryDiagnosticCode.UNUSUAL_CONTAINER_ID,
                        entry,
                    )
                )
            if not bank_names:
                diagnostics.append(
                    DiscoveryDiagnostic(
                        DiscoveryDiagnosticCode.NO_PAYLOAD,
                        entry,
                    )
                )
            if not metadata_names:
                diagnostics.append(
                    DiscoveryDiagnostic(
                        DiscoveryDiagnosticCode.NO_METADATA,
                        entry,
                    )
                )
            saves.append(DiscoveredSave(self.provider_id, entry))

        return DiscoveryReport(tuple(saves), tuple(diagnostics))

    @staticmethod
    def _get_bank_names(container: Path, diagnostics: list[DiscoveryDiagnostic]) -> tuple[str, ...]:
        """Return names of the existing `0` and `1` payload directories.

        Historical Ryujinx calls `0` committed and `1` working; these are not
        game save slots. Presence alone does not validate either directory or
        decide which tree Ryujinx would mount now. The scanner does not enter
        them. A link is skipped and reported through ``diagnostics``.
        """
        names: list[str] = []
        for name in _BANK_NAMES:
            bank = container / name
            if bank.is_symlink():
                diagnostics.append(
                    DiscoveryDiagnostic(DiscoveryDiagnosticCode.SYMLINK_SKIPPED, bank)
                )
            elif bank.is_dir():
                names.append(name)
        return tuple(names)

    @staticmethod
    def _get_metadata_names(
        container: Path, diagnostics: list[DiscoveryDiagnostic]
    ) -> tuple[str, ...]:
        """Return names of existing `ExtraData0` and `ExtraData1` files.

        The files are siblings of the payload directories. This only checks
        their presence and type; it does not read or interpret their contents.
        A link is skipped and reported through ``diagnostics``.
        """
        names: list[str] = []
        for name in _METADATA_NAMES:
            metadata = container / name
            if metadata.is_symlink():
                diagnostics.append(
                    DiscoveryDiagnostic(DiscoveryDiagnosticCode.SYMLINK_SKIPPED, metadata)
                )
            elif metadata.is_file():
                names.append(name)
        return tuple(names)
