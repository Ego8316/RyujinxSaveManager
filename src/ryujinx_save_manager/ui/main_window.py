"""Phase 0 read-only application shell."""

from PySide6.QtWidgets import QLabel, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("RyujinxSaveManager — Phase 0")
        self.resize(800, 500)
        self.setCentralWidget(
            QLabel("Repository foundation ready. Save discovery is not implemented yet.")
        )
