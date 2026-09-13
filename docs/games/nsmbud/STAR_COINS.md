# Star Coin observations

At observed slot-relative `0x128`, entries are packed as nibbles, two levels per byte (**HIGH CONFIDENCE** for tested entries). `0x7` was observed when all three Star Coins were collected (**TENTATIVE** as a complete encoding rule). The nibble order and meanings of other values require further evidence. Any future single-entry edit must preserve the neighboring nibble exactly and update documented integrity bytes. See [known mappings](LEVEL_MAPPING.md) and [checksum](CHECKSUM.md).
