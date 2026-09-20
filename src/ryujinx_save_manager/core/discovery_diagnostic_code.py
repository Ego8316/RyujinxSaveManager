"""Stable, format-neutral diagnostic codes for save discovery."""

# standard imports
from enum import StrEnum


class DiscoveryDiagnosticCode(StrEnum):
    SYMLINK_SKIPPED = "symlink_skipped"
    UNREADABLE = "unreadable"
    UNRECOGNIZED_CONTAINER = "unrecognized_container"
    UNUSUAL_CONTAINER_ID = "unusual_container_id"
    NO_PAYLOAD = "no_payload"
    NO_METADATA = "no_metadata"

    @property
    def message(self) -> str:
        """Default user-facing text; provider-specific details stay in the diagnostic."""
        match self:
            case DiscoveryDiagnosticCode.SYMLINK_SKIPPED:
                return "Symbolic link skipped"
            case DiscoveryDiagnosticCode.UNREADABLE:
                return "Could not read entry"
            case DiscoveryDiagnosticCode.UNRECOGNIZED_CONTAINER:
                return "No recognized payload or metadata entries found"
            case DiscoveryDiagnosticCode.UNUSUAL_CONTAINER_ID:
                return "Container name does not match the expected save ID format"
            case DiscoveryDiagnosticCode.NO_PAYLOAD:
                return "No recognized payload directory found"
            case DiscoveryDiagnosticCode.NO_METADATA:
                return "No recognized metadata file found"
        raise AssertionError(f"Missing message for discovery code {self.value}")
