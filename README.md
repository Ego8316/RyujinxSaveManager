# RyujinxSaveManager

A local Windows and Linux desktop application planned to discover, back up, inspect, restore, and edit Ryujinx saves without asking users to understand Ryujinx's save directory layout. The current application can select a Ryujinx save root and list structurally recognizable containers without editing them. Game names and Title IDs are not decoded yet. WSL is the primary development environment.

## Development from WSL

Use Python 3.12 or newer and WSLg if you want to launch the GUI. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/check.py
ryujinx-save-manager
```

If `python` is older than 3.12, install a newer interpreter first, then use its executable to create `.venv` (for example `python3.12 -m venv .venv`). The quality checks work headlessly; opening the app requires a graphical session. `python -m ryujinx_save_manager` is an equivalent entry point. On Windows or another Linux setup, activate the virtual environment using that platform's usual command; the remaining commands are the same.

The application accepts a user-selected Ryujinx `bis/user/save` directory rather than relying on a fixed OS path. This includes Windows directories mounted under WSL, such as `/mnt/c/Users/.../`.

Start with [product scope](docs/PRODUCT.md), [architecture](docs/ARCHITECTURE.md), and [save safety](docs/SAVE_SAFETY.md). Contributors and coding agents must read [AGENTS.md](AGENTS.md). The [roadmap](docs/ROADMAP.md) separates current capability from planned work.

The project source is MIT licensed. Game names and trademarks belong to their owners; third-party game assets and user save data are not covered by this license.
