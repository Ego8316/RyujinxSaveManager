# Known unknowns

The number and kind of slots, complete file layout, header meaning, slot ownership, all other level mappings, bit semantics of level states, Star Coin nibble order and non-`0x7` meanings, CRC behavior across all slots, and whether file size varies are **UNKNOWN**. There may be additional integrity or metadata rules. `ExtraData0` may coexist in a Ryujinx container, but its game-specific meaning is not established here. Do not implement writes from these notes alone; seek independent observations and synthetic tests first.
