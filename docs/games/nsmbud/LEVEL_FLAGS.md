# Observed level-state values

At the observed slot-relative table offset `0x6F`, these values appeared in test saves. Meanings remain **TENTATIVE** outside the observed cases:

| Value | Observed interpretation |
| --- | --- |
| `0x00` | unavailable / not unlocked |
| `0x01` | unlocked but not completed |
| `0x43` | normally completed |
| `0xC3` | completed secret-exit state in one observation |

The bit-level meaning and any other values are **UNKNOWN**. Do not assume a general flags mask or apply these meanings to unverified levels. See [known mappings](LEVEL_MAPPING.md).
