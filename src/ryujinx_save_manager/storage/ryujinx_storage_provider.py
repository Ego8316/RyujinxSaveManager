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
    SaveType,
)
from ryujinx_save_manager.storage.extra_data_header import ExtraDataHeader
from ryujinx_save_manager.storage.save_data_type import SaveDataType

_CONTAINER_ID = re.compile(r"[0-9a-fA-F]{16}\Z")
_BANK_NAMES = ("0", "1")
_METADATA_NAMES = ("ExtraData0", "ExtraData1")


class RyujinxStorageProvider:
    """Scan a selected `bis/user/save` directory one level deep.

    Folder names are emulator SaveDataIds, never presumed game Title IDs.
    Original Ryujinx source uses `0` for committed data and `1` for working
    data; discovery checks only their presence. Metadata is parsed separately
    and never modified.
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
            title_id = None
            save_data_type: SaveType | None = None
            if not metadata_names:
                diagnostics.append(
                    DiscoveryDiagnostic(
                        DiscoveryDiagnosticCode.NO_METADATA,
                        entry,
                    )
                )
            else:
                title_id, save_data_type = self._inspect_metadata(
                    entry, metadata_names, diagnostics
                )
            saves.append(
                DiscoveredSave(
                    self.provider_id,
                    entry,
                    title_id=title_id,
                    save_data_id=entry.name.upper() if canonical_id else None,
                    save_data_type=save_data_type,
                )
            )

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
    def _inspect_metadata(
        container: Path,
        names: tuple[str, ...],
        diagnostics: list[DiscoveryDiagnostic],
    ) -> tuple[str | None, SaveType | None]:
        """Read available ExtraData files and reconcile their save identity.

        ``names`` contains the regular metadata files found in ``container``.
        Each file must have the documented size; read or size failures append
        a diagnostic. Two successfully parsed copies must agree on Application
        ID, AccountUid, SystemSaveDataId, and save-data type. Otherwise this
        returns ``(None, None)`` and reports a conflict when copies disagree.

        Agreement yields the nonzero Application ID as uppercase hex (or
        ``None`` for zero) and a provider-neutral save type. This is only a
        discovery decision: neither metadata copy is treated as authoritative
        for transactions, and this method never modifies either file.
        """
        headers: list[ExtraDataHeader] = []
        for name in names:
            path = container / name
            try:
                headers.append(ExtraDataHeader.from_path(path))
            except ValueError as exc:
                diagnostics.append(
                    DiscoveryDiagnostic(
                        DiscoveryDiagnosticCode.INVALID_METADATA_SIZE, path, detail=str(exc)
                    )
                )
            except OSError as exc:
                diagnostics.append(
                    DiscoveryDiagnostic(DiscoveryDiagnosticCode.UNREADABLE, path, detail=str(exc))
                )
        if len(headers) == 2 and headers[0].identity != headers[1].identity:
            diagnostics.append(
                DiscoveryDiagnostic(DiscoveryDiagnosticCode.CONFLICTING_METADATA, container)
            )
            return None, None
        if len(headers) == 2:
            raw_type = headers[0].save_data_type
            label = (
                raw_type.label if isinstance(raw_type, SaveDataType) else f"Unknown ({raw_type})"
            )
            return headers[0].application_id_hex, SaveType(int(raw_type), label)
        return None, None

    @staticmethod
    def _get_metadata_names(
        container: Path, diagnostics: list[DiscoveryDiagnostic]
    ) -> tuple[str, ...]:
        """Return names of existing `ExtraData0` and `ExtraData1` files.

        The files are siblings of the payload directories. This only checks
        their presence and type; content inspection happens separately.
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
