"""Read-only root selection and discovered-save presentation."""

# standard imports
from pathlib import Path

# 1st-party imports
from ryujinx_save_manager.core.discovery_service import DiscoveryService
from ryujinx_save_manager.core.models import DiscoveryReport

# 3rd-party imports
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self, discovery: DiscoveryService) -> None:
        super().__init__()
        self._discovery = discovery
        self.setWindowTitle("RyujinxSaveManager")
        self.resize(800, 500)

        central = QWidget()
        layout = QVBoxLayout(central)
        self._choose_button = QPushButton("Choose Ryujinx save directory")
        self._choose_button.clicked.connect(self._choose_root)
        self._root_label = QLabel("Select a Ryujinx bis/user/save directory to discover saves.")
        self._save_list = QListWidget()
        self._diagnostic_list = QListWidget()
        self._status_label = QLabel("Read-only discovery. No save files will be changed.")
        layout.addWidget(self._choose_button)
        layout.addWidget(self._root_label)
        layout.addWidget(self._save_list)
        layout.addWidget(QLabel("Discovery diagnostics"))
        layout.addWidget(self._diagnostic_list)
        layout.addWidget(self._status_label)
        self.setCentralWidget(central)

    def _choose_root(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Choose Ryujinx save directory")
        if selected:
            self.scan_root(Path(selected))

    def scan_root(self, root: Path) -> None:
        """Present a service result; directory traversal stays outside the UI."""
        self._root_label.setText(f"Selected directory: {root}")
        try:
            report = self._discovery.scan(root)
        except (OSError, ValueError) as exc:
            self._save_list.clear()
            self._diagnostic_list.clear()
            self._status_label.setText(f"Could not scan directory: {exc}")
            return
        self._present(report)

    def _present(self, report: DiscoveryReport) -> None:
        self._save_list.clear()
        self._diagnostic_list.clear()
        for save in report.saves:
            label = save.display_name or f"Unidentified save ({save.container_path.name})"
            self._save_list.addItem(label)
        for diagnostic in report.diagnostics:
            self._diagnostic_list.addItem(f"{diagnostic.path.name}: {diagnostic.message}")
        self._status_label.setText(
            f"{len(report.saves)} save container(s), {len(report.diagnostics)} diagnostic(s). "
            "Title IDs are not decoded yet."
        )
