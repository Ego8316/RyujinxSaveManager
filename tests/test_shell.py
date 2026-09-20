"""Headless smoke coverage for read-only root selection and presentation."""

# standard imports
from pathlib import Path

# 1st-party imports
from ryujinx_save_manager import __main__
from ryujinx_save_manager.core.discovery_service import DiscoveryService
from ryujinx_save_manager.storage.ryujinx_storage_provider import RyujinxStorageProvider
from ryujinx_save_manager.ui.main_window import MainWindow

# 3rd-party imports
import pytest
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QPushButton


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> QApplication:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    return application


def test_shell_displays_unidentified_saves_and_diagnostics(
    app: QApplication, tmp_path: Path
) -> None:
    assert QApplication.instance() is app
    container = tmp_path / "0000000000000001"
    (container / "0").mkdir(parents=True)
    window = MainWindow(DiscoveryService(RyujinxStorageProvider()))
    window.scan_root(tmp_path)

    assert window.windowTitle() == "RyujinxSaveManager"
    lists = window.findChildren(QListWidget)
    assert len(lists) == 2
    assert lists[0].item(0).text() == "SaveDataId 0000000000000001 · Unidentified"
    assert "No recognized metadata file found" in lists[1].item(0).text()
    assert any("1 save container" in label.text() for label in window.findChildren(QLabel))
    window.close()


def test_shell_reports_invalid_root(app: QApplication, tmp_path: Path) -> None:
    assert QApplication.instance() is app
    window = MainWindow(DiscoveryService(RyujinxStorageProvider()))
    window.scan_root(tmp_path / "missing")
    assert any("Could not scan" in label.text() for label in window.findChildren(QLabel))
    window.close()


def test_shell_shows_application_and_save_type(app: QApplication, tmp_path: Path) -> None:
    assert QApplication.instance() is app
    container = tmp_path / "0000000000000001"
    container.mkdir()
    data = bytearray(0x200)
    data[:8] = (0x01006F8002326000).to_bytes(8, "little")
    data[0x20] = 3
    (container / "ExtraData0").write_bytes(data)
    (container / "ExtraData1").write_bytes(data)
    window = MainWindow(DiscoveryService(RyujinxStorageProvider()))
    window.scan_root(tmp_path)

    save_list = window.findChildren(QListWidget)[0]
    assert save_list.item(0).text() == (
        "SaveDataId 0000000000000001 · Application ID: 01006F8002326000 · Save type: Device"
    )
    window.close()


def test_choose_button_passes_selected_directory_to_service(
    app: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert QApplication.instance() is app
    window = MainWindow(DiscoveryService(RyujinxStorageProvider()))
    monkeypatch.setattr(
        "ryujinx_save_manager.ui.main_window.QFileDialog.getExistingDirectory",
        lambda *_args: str(tmp_path),
    )
    button = window.findChild(QPushButton)
    assert button is not None
    button.click()
    assert any(str(tmp_path) in label.text() for label in window.findChildren(QLabel))
    window.close()


def test_entry_point_returns_event_loop_code(monkeypatch: pytest.MonkeyPatch) -> None:
    shown: list[bool] = []

    class StubApplication:
        def __init__(self, argv: list[str]) -> None:
            assert argv

        def exec(self) -> int:
            return 42

    class StubWindow:
        def __init__(self, discovery: DiscoveryService) -> None:
            assert isinstance(discovery.provider, RyujinxStorageProvider)

        def show(self) -> None:
            shown.append(True)

    monkeypatch.setattr(__main__, "QApplication", StubApplication)
    monkeypatch.setattr(__main__, "MainWindow", StubWindow)
    assert __main__.main() == 42
    assert shown == [True]
