# Roadmap

**Phase 0 (complete):** documentation, package boundaries, contracts, generic byte diff, tests, and a read-only shell.

**Phase 1 (in progress):** manual root selection, a conservative read-only Ryujinx container scanner, diagnostics, and synthetic tests are implemented. The scanner checks `ExtraData` size and matching identity fields and exposes Application ID plus save-data type where both copies agree; little-endian decoding was checked against private Account, Device, and BCAT observations. Next, resolve friendly game names separately, investigate AccountUid representation and single-copy metadata policy, and then add reliable automatic root suggestions and optional remembered selection. Do not begin write support in this phase by accident.

**Later:** verified snapshot/restore engine and failure tests; transaction service with crash/rollback design; read-only game plugin and format validation; only then constrained NSMBU Deluxe editing and specialized UI. Raw diff can grow from individual byte changes into contiguous ranges and optional plugin explanations. Windows and Linux packaging follows tested core behavior and stays separate from save-management logic.
