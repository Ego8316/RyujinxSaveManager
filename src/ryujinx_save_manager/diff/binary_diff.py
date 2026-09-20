"""Format-neutral comparison of byte strings."""

# standard imports
from dataclasses import dataclass
from itertools import zip_longest


@dataclass(frozen=True, slots=True)
class ByteChange:
    offset: int
    before: int | None
    after: int | None


def compare_bytes(before: bytes, after: bytes) -> tuple[ByteChange, ...]:
    """Report each changed byte; None denotes an absent byte after a size change."""
    return tuple(
        ByteChange(offset, old, new)
        for offset, (old, new) in enumerate(zip_longest(before, after))
        if old != new
    )
