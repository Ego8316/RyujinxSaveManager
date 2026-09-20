"""Synthetic, read-only Ryujinx directory discovery tests."""

# standard imports
from pathlib import Path

# 1st-party imports
from ryujinx_save_manager.core.discovery_diagnostic_code import DiscoveryDiagnosticCode
from ryujinx_save_manager.storage.ryujinx_storage_provider import RyujinxStorageProvider

# 3rd-party imports
import pytest


def test_discovers_numbered_container_without_claiming_title_id(tmp_path: Path) -> None:
    container = tmp_path / "0000000000000001"
    (container / "0").mkdir(parents=True)
    (container / "0" / "synthetic.txt").write_text("sample")
    (container / "ExtraData0").write_bytes(b"synthetic metadata")
    before = (container / "ExtraData0").read_bytes()

    report = RyujinxStorageProvider().discover(tmp_path)

    assert len(report.saves) == 1
    save = report.saves[0]
    assert save.container_path == container
    assert save.title_id is None
    assert save.user_id is None
    assert report.diagnostics == ()
    assert (container / "ExtraData0").read_bytes() == before


def test_partial_and_unusual_containers_produce_diagnostics(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("unrelated")
    (tmp_path / "empty").mkdir()
    (tmp_path / "custom" / "1").mkdir(parents=True)
    (tmp_path / "0000000000000002").mkdir()
    (tmp_path / "0000000000000002" / "ExtraData1").write_bytes(b"metadata")

    report = RyujinxStorageProvider().discover(tmp_path)

    assert {save.container_path.name for save in report.saves} == {
        "custom",
        "0000000000000002",
    }
    codes = {diagnostic.code for diagnostic in report.diagnostics}
    assert codes == {
        DiscoveryDiagnosticCode.UNRECOGNIZED_CONTAINER,
        DiscoveryDiagnosticCode.UNUSUAL_CONTAINER_ID,
        DiscoveryDiagnosticCode.NO_PAYLOAD,
        DiscoveryDiagnosticCode.NO_METADATA,
    }


def test_canonical_empty_container_remains_visible(tmp_path: Path) -> None:
    container = tmp_path / "0000000000000003"
    container.mkdir()

    report = RyujinxStorageProvider().discover(tmp_path)

    assert [save.container_path for save in report.saves] == [container]
    assert {diagnostic.code for diagnostic in report.diagnostics} == {
        DiscoveryDiagnosticCode.UNRECOGNIZED_CONTAINER,
        DiscoveryDiagnosticCode.NO_PAYLOAD,
        DiscoveryDiagnosticCode.NO_METADATA,
    }


def test_invalid_root_is_rejected(tmp_path: Path) -> None:
    provider = RyujinxStorageProvider()
    with pytest.raises(ValueError, match="Not a readable directory"):
        provider.discover(tmp_path / "missing")
    file = tmp_path / "file"
    file.write_text("x")
    with pytest.raises(ValueError, match="Not a readable directory"):
        provider.discover(file)


def test_symlink_container_is_skipped(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    (outside / "0").mkdir(parents=True)
    root = tmp_path / "save"
    root.mkdir()
    link = root / "0000000000000001"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Creating directory symlinks is unavailable on this platform")

    report = RyujinxStorageProvider().discover(root)
    assert report.saves == ()
    assert [diagnostic.code for diagnostic in report.diagnostics] == [
        DiscoveryDiagnosticCode.SYMLINK_SKIPPED
    ]
    assert report.diagnostics[0].code.value == "symlink_skipped"
    assert report.diagnostics[0].message == "Symbolic link skipped"


def test_unfamiliar_container_link_is_reported(tmp_path: Path) -> None:
    container = tmp_path / "0000000000000001"
    (container / "0").mkdir(parents=True)
    link = container / "unfamiliar-link"
    try:
        link.symlink_to(tmp_path / "outside")
    except OSError:
        pytest.skip("Creating symlinks is unavailable on this platform")

    report = RyujinxStorageProvider().discover(tmp_path)

    assert [save.container_path for save in report.saves] == [container]
    assert any(
        diagnostic.code == DiscoveryDiagnosticCode.SYMLINK_SKIPPED and diagnostic.path == link
        for diagnostic in report.diagnostics
    )


def test_one_unreadable_container_does_not_hide_others(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad = tmp_path / "0000000000000001"
    good = tmp_path / "0000000000000002"
    (bad / "0").mkdir(parents=True)
    (good / "0").mkdir(parents=True)
    original_is_dir = Path.is_dir

    def simulated_is_dir(path: Path) -> bool:
        if path == bad:
            raise PermissionError("synthetic access denied")
        return original_is_dir(path)

    monkeypatch.setattr(Path, "is_dir", simulated_is_dir)
    report = RyujinxStorageProvider().discover(tmp_path)

    assert [save.container_path for save in report.saves] == [good]
    assert any(
        diagnostic.code == DiscoveryDiagnosticCode.UNREADABLE and diagnostic.path == bad
        for diagnostic in report.diagnostics
    )
    assert report.diagnostics[0].message == "Could not read entry: synthetic access denied"
