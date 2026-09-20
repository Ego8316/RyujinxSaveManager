# Product scope

RyujinxSaveManager should let a user choose a Ryujinx save root such as `Ryujinx/bis/user/save/`, then browse discovered saves by recognizable game and user labels where evidence permits. The user should not have to navigate emulator internals. Planned workflows are inspection, automatic backup, restore, raw diff, and game-specific editing through bundled plugins. Everything runs locally; Windows and Linux are supported application targets, and WSL is the primary development environment.

The current application can select a root and list structurally recognizable save containers with diagnostics. Game names and Title IDs are still unknown, and no save parsing or writing is enabled. See [roadmap](ROADMAP.md) for the next increments and [UI/UX](UI_UX.md) for navigation direction.
