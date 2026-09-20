# Architecture

The `src/ryujinx_save_manager` package separates format-neutral services from game knowledge:

- `core` contains normalized save identity models.
- `storage` performs conservative, read-only Ryujinx container discovery from a selected root, parses bounded `ExtraData` metadata separately, and reports diagnostics.
- `backup` currently defines manifest metadata only. A transaction service must own all writes before any editing is enabled.
- `plugins` defines bundled game-plugin detection and registration. No game plugin ships yet.
- `diff` compares bytes without assigning meaning.
- `ui` is a code-first PySide6 root chooser and read-only result view. It calls the discovery service rather than traversing directories itself; future write requests must also pass through application services.

The implemented discovery flow is UI-selected root → discovery service → storage provider → normalized saves and diagnostics → UI. Switch save-data type codes and their enum live inside the Ryujinx storage package; the normalized core model carries only a provider-neutral code and display label. A future editing flow is UI intent → application service → verified backup and transactional writer → plugin transform/validation. Plugins may parse a private game model, but the core must not import game format modules. The transaction owner must validate plugin-provided output before committing. Provider paths and plugin file lists are untrusted inputs requiring containment checks before copying or writing.

See [plugin API](PLUGIN_API.md), [storage](RYUJINX_STORAGE.md), [save safety](SAVE_SAFETY.md), and [UI/UX](UI_UX.md). These documents describe intended contracts, not implemented write guarantees.
