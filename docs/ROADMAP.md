# Roadmap

**Phase 0 (current):** documentation, package boundaries, contracts, generic byte diff, tests, and a read-only shell. No real save editing or discovery.

**Phase 1 (next):** research Ryujinx container layout with synthetic and consented private fixtures, then implement read-only root selection, discovery, and identification diagnostics. Preserve uncertainty in metadata interpretation. Do not begin write support in this phase by accident.

**Later:** verified snapshot/restore engine and failure tests; transaction service with crash/rollback design; read-only game plugin and format validation; only then constrained NSMBU Deluxe editing and specialized UI. Raw diff can grow from individual byte changes into contiguous ranges and optional plugin explanations. Windows and Linux packaging follows tested core behavior and stays separate from save-management logic.
