"""Read-only inspection of the documented Ryujinx ExtraData attribute header."""

from __future__ import annotations

# standard imports
from dataclasses import dataclass
from pathlib import Path

# 1st-party imports
from ryujinx_save_manager.storage.save_data_type import SaveDataType

EXTRA_DATA_SIZE = 0x200


@dataclass(frozen=True, slots=True)
class ExtraDataHeader:
    """Identity fields from a size-checked Ryujinx metadata structure.

    The Application ID is decoded explicitly as little-endian. Account UID
    stays raw because its user-facing representation is not yet established.
    """

    application_id: int
    account_uid_bytes: bytes
    system_save_data_id_bytes: bytes
    save_data_type: SaveDataType | int

    @classmethod
    def from_bytes(cls, data: bytes) -> ExtraDataHeader:
        """Require the documented 0x200-byte structure before reading fields."""
        if len(data) != EXTRA_DATA_SIZE:
            raise ValueError(f"Expected {EXTRA_DATA_SIZE} metadata bytes, found {len(data)}")
        raw_type = data[0x20]
        try:
            save_data_type: SaveDataType | int = SaveDataType(raw_type)
        except ValueError:
            save_data_type = raw_type
        return cls(
            int.from_bytes(data[0x00:0x08], "little"),
            data[0x08:0x18],
            data[0x18:0x20],
            save_data_type,
        )

    @classmethod
    def from_path(cls, path: Path) -> ExtraDataHeader:
        """Read at most one byte past the expected size to bound scan memory."""
        with path.open("rb") as stream:
            return cls.from_bytes(stream.read(EXTRA_DATA_SIZE + 1))

    @property
    def identity(self) -> tuple[int, bytes, bytes, SaveDataType | int]:
        """Fields expected to identify the same save across metadata copies."""
        return (
            self.application_id,
            self.account_uid_bytes,
            self.system_save_data_id_bytes,
            self.save_data_type,
        )

    @property
    def application_id_hex(self) -> str | None:
        """Render a nonzero Application ID as canonical uppercase hexadecimal."""
        if self.application_id == 0:
            return None
        return f"{self.application_id:016X}"
