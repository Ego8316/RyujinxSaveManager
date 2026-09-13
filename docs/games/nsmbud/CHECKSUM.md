# Slot checksum observation

In the observed slot, the final four bytes contain CRC32 of the slot excluding those four bytes, stored big-endian (**HIGH CONFIDENCE** for the tested slot). With slot size `0x208`, the checksum bytes are at slot-relative `0x204..0x207`; for the first observed slot beginning at `0x10`, that is absolute `0x214..0x217`. This arithmetic does not prove other slots share the layout. CRC variant details and applicability to every slot need independent fixture-backed tests before editing. Phase 0 does not calculate or write this checksum.
