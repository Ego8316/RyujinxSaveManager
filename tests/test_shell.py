"""Headless smoke coverage for the read-only Qt shell."""

import pytest
from PySide6.QtWidgets import QApplication, QLabel

from ryujinx_save_manager import __main__
from ryujinx_save_manager.ui.main_window import MainWindow


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> QApplication:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    return application


def test_shell_is_explicitly_read_only(app: QApplication) -> None:
    assert QApplication.instance() is app
    window = MainWindow()
    assert window.windowTitle() == "RyujinxSaveManager — Phase 0"
    label = window.centralWidget()
    assert isinstance(label, QLabel)
    assert "Save discovery is not implemented" in label.text()
    window.close()


def test_entry_point_returns_event_loop_code(monkeypatch: pytest.MonkeyPatch) -> None:
    shown: list[bool] = []

    class StubApplication:
        def __init__(self, argv: list[str]) -> None:
            assert argv

        def exec(self) -> int:
            return 42

    class StubWindow:
        def show(self) -> None:
            shown.append(True)

    monkeypatch.setattr(__main__, "QApplication", StubApplication)
    monkeypatch.setattr(__main__, "MainWindow", StubWindow)
    assert __main__.main() == 42
    assert shown == [True]
