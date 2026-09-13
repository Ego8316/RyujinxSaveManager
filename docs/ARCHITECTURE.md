# Architecture

The `src/ryujinx_save_manager` package separates format-neutral services from game knowledge:

- `core` contains normalized save identity models.
- `storage` defines read-only discovery from a selected root. The Ryujinx implementation is planned, not present.
- `backup` currently defines manifest metadata only. A transaction service must own all writes before any editing is enabled.
- `plugins` defines bundled game-plugin detection and registration. No game plugin ships yet.
- `diff` compares bytes without assigning meaning.
- `ui` is a read-only PySide6 shell. Future views are code-first, composable widgets; UI requests must pass through application services when those services exist.

A future flow is provider discovery → normalized save → matching plugin → read-only inspection, or, for edits, UI intent → application service → verified backup and transactional writer → plugin transform/validation. Plugins may parse a private game model, but the core must not import game format modules. The transaction owner must validate plugin-provided output before committing. Provider paths and plugin file lists are untrusted inputs requiring containment checks before copying or writing.

See [plugin API](PLUGIN_API.md), [storage](RYUJINX_STORAGE.md), [save safety](SAVE_SAFETY.md), and [UI/UX](UI_UX.md). These documents describe intended contracts, not implemented write guarantees.
