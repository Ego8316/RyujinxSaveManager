"""Known Switch save-data types; unknown numeric values remain valid raw data."""

# standard imports
from enum import IntEnum


class SaveDataType(IntEnum):
    SYSTEM = 0
    ACCOUNT = 1
    BCAT = 2
    DEVICE = 3
    TEMPORARY = 4
    CACHE = 5
    SYSTEM_BCAT = 6

    @property
    def label(self) -> str:
        """Short user-facing name without exposing an enum implementation detail."""
        if self == SaveDataType.BCAT:
            return "BCAT"
        if self == SaveDataType.SYSTEM_BCAT:
            return "System BCAT"
        return self.name.title()
