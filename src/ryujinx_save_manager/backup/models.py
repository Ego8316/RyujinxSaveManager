"""Backup metadata contract; the backup engine is not implemented yet."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class BackupFile:
    relative_path: Path
    size: int
    sha256: str


@dataclass(frozen=True, slots=True)
class BackupManifest:
    source_path: Path
    created_at: datetime
    title_id: str | None
    application_version: str
    files: tuple[BackupFile, ...]
