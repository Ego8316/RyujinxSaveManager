# Reverse-engineering discipline

Never silently guess a binary field. Record offset, size, encoding, meaning, evidence/source, confidence, observed values, unknown values, and integrity implications. Use **CONFIRMED** for independently reproduced facts, **HIGH CONFIDENCE** for strong repeated evidence, **TENTATIVE** for limited observations, and **UNKNOWN** where evidence is absent. An implementation or a prior note is not itself proof.

Keep raw observations distinct from interpretations. Preserve unknown bytes exactly and never silently “repair” them. A changed byte without a verified meaning remains unknown in generic diff output. Add or revise tests and game notes together when new evidence arrives. The [NSMBU Deluxe notes](games/nsmbud/FORMAT.md) are initial observations, not a complete specification.
