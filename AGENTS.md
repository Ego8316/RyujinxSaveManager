# Instructions for coding agents

Read the relevant documents under `docs/` before editing code. In particular, read `docs/SAVE_SAFETY.md` for any work involving writes, `docs/PLUGIN_API.md` for plugin changes, and `docs/REVERSE_ENGINEERING.md` for binary formats. Check this file against the actual repository rather than assuming a planned feature exists.

Correctness and data safety outrank convenience. Treat user saves as valuable and potentially irreplaceable. Preserve the invariant that a failed edit cannot destroy or corrupt the original. Every write to an existing save requires a verified backup first; if backup creation or verification fails, abort. There must never be a bypass or “continue anyway” option. Prefer reversible operations.

Keep game-specific parsing, fields, checksums, and UI inside game plugins. The core and storage providers must remain format-agnostic. Never invent offsets or silently repair unknown data. Preserve unknown bytes exactly. Distinguish confirmed knowledge from assumptions, record evidence and confidence, and update format documentation when new knowledge is discovered.

When a module primarily contains one class, name the file after that class in `snake_case` (for example, `discovery_service.py` for `DiscoveryService`). Keep cohesive groups of models or a class with closely related functions together when that makes the module clearer.

Let Ruff sort imports and maintain section comments: `# standard imports`, `# 1st-party imports`, `# 3rd-party imports`, and `# local imports` when those sections are present. Project package imports are first-party; relative imports are local. Run `ruff check --fix .` to apply import ordering before the final quality gate.

Add meaningful tests for binary parsing or writing changes: verify exact changed offsets, preservation of unrelated bytes, endianness, checksums, and failure behavior. Use synthetic fixtures by default; do not commit real saves or proprietary assets. Run relevant tests before declaring work complete. Minimize unrelated changes. The current discovery UI is read-only; do not describe planned write paths or unverified Title ID decoding as implemented.

## Quality gate and platforms

WSL is the canonical development environment; the application supports Windows and Linux. Use portable `pathlib.Path` handling and accept a caller-provided Ryujinx directory, which may live on a Windows-mounted volume under WSL. Core tests must run headlessly without a `QApplication` or a real save. Before declaring a coding task complete, run `python scripts/check.py` (Ruff lint, Ruff format check, strict mypy, and pytest with at least 80% coverage) and fix applicable failures. Do not suppress warnings merely to obtain a green build. CI runs the same gates on Ubuntu and Windows with Python 3.12. If an environment cannot run them, state precisely what remains unverified.

## UI implementation

Follow [docs/UI_UX.md](docs/UI_UX.md): write PySide6 views as small composable Python widgets, use Qt layouts for structure, QSS for appearance, and shared metrics only when useful. Qt Designer files are exceptions that need a concrete reason. Widgets emit intent and display results; they never traverse, parse, back up, or write saves. Plugin widgets may be game-specific but use the same service boundary. Keep core tests independent of `QApplication` and UI tests headless.
