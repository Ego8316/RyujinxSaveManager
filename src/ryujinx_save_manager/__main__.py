"""Application entry point."""

import logging
import sys

from PySide6.QtWidgets import QApplication

from ryujinx_save_manager.ui.main_window import MainWindow


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
