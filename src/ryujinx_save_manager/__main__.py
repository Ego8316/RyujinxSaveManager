"""Application entry point."""

# standard imports
import logging
import sys

# 1st-party imports
from ryujinx_save_manager.core.discovery_service import DiscoveryService
from ryujinx_save_manager.storage.ryujinx_storage_provider import RyujinxStorageProvider
from ryujinx_save_manager.ui.main_window import MainWindow

# 3rd-party imports
from PySide6.QtWidgets import QApplication


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)
    discovery = DiscoveryService(RyujinxStorageProvider())
    window = MainWindow(discovery)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
