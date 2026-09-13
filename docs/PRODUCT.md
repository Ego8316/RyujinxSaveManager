# Product scope

RyujinxSaveManager should let a user choose a Ryujinx save root such as `Ryujinx/bis/user/save/`, then browse discovered saves by recognizable game and user labels where evidence permits. The user should not have to navigate emulator internals. Planned workflows are inspection, automatic backup, restore, raw diff, and game-specific editing through bundled plugins. Everything runs locally; Windows and Linux are supported application targets, and WSL is the primary development environment.

Phase 0 only supplies a read-only shell and architecture contracts. No real saves are scanned or edited. See [roadmap](ROADMAP.md) for the next increments and [UI/UX](UI_UX.md) for the intended navigation.
