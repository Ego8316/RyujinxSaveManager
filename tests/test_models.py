"""Contracts shared by storage and future backup services."""

# standard imports
from datetime import UTC, datetime
from pathlib import Path

# 1st-party imports
from ryujinx_save_manager.backup.models import BackupFile, BackupManifest
from ryujinx_save_manager.core.discovery_service import DiscoveryService
from ryujinx_save_manager.core.models import DiscoveredSave, DiscoveryReport
from ryujinx_save_manager.storage.storage_provider import StorageProvider


def test_backup_manifest_retains_relative_files_and_hashes(tmp_path: Path) -> None:
    file = BackupFile(Path("ExtraData0"), 4, "a" * 64)
    manifest = BackupManifest(
        source_path=tmp_path,
        created_at=datetime(2026, 9, 13, tzinfo=UTC),
        title_id=None,
        application_version="0.1.0",
        files=(file,),
    )
    assert manifest.files[0].relative_path == Path("ExtraData0")
    assert manifest.files[0].sha256 == "a" * 64


def test_storage_contract_accepts_caller_supplied_root(tmp_path: Path) -> None:
    class SyntheticProvider:
        provider_id = "synthetic"

        def discover(self, root: Path) -> DiscoveryReport:
            return DiscoveryReport((DiscoveredSave(self.provider_id, root / "container"),), ())

    provider: StorageProvider = SyntheticProvider()
    report = DiscoveryService(provider).scan(tmp_path)
    assert report.saves[0].container_path == tmp_path / "container"
