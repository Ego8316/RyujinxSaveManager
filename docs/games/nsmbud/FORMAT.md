# NSMBU Deluxe: observed file format

This is a research log, not an editor specification. Observed save filename: `rp_savedata.dat` (**HIGH CONFIDENCE**, one known game-specific filename). One valid observed file began with ASCII `RPSD` and measured 49,780 bytes (**TENTATIVE** as a universal size/signature requirement). The first Mario slot began at `0x10`, with observed slot size `0x208` (**TENTATIVE** beyond the tested save). Do not infer all slot counts or layouts from this.

The level-state table was observed at slot-relative `0x6F`; Star Coin data at slot-relative `0x128` (**TENTATIVE** beyond observed samples). The last four slot bytes are a CRC32, discussed in [CHECKSUM.md](CHECKSUM.md). No parser or editor implements these facts in Phase 0. Cross-check all changes against [reverse-engineering discipline](../../REVERSE_ENGINEERING.md).
