# Roadmap

**Phase 0 (complete):** documentation, package boundaries, contracts, generic byte diff, tests, and a read-only shell.

**Phase 1 (in progress):** manual root selection, a conservative read-only Ryujinx container scanner, diagnostics, and synthetic tests are implemented. Next, verify `ExtraData0` layout against independently obtained private fixtures before assigning Title IDs or users; then add reliable automatic root suggestions and optional remembered selection. Do not begin write support in this phase by accident.

**Later:** verified snapshot/restore engine and failure tests; transaction service with crash/rollback design; read-only game plugin and format validation; only then constrained NSMBU Deluxe editing and specialized UI. Raw diff can grow from individual byte changes into contiguous ranges and optional plugin explanations. Windows and Linux packaging follows tested core behavior and stays separate from save-management logic.
