# Hashkey Standalone — Architecture
## Date: March 15 2026
## Author: Anthony Hagerty — Haskell Texas

## Purpose
Standalone networkless data transfer system.
Independent of AIA. No AI dependency. Pure data transport.

## Pipeline
Any data → 6-base pair fold encoder → JSON sealed inside fold
→ 4-base pair hash address generated
→ phone number key generated
→ hash + key transmit (KB regardless of data size)
→ receiver state machine: hash + key → fold drops open
→ JSON self-present → data rebuilds onsite
→ hash integrity verified — no extra files needed

## Token Structure
6-base pair fold (sender side):
A  — AM frequency binary   (16 bits)
T  — RGB color binary      (24 bits)  — single 8-bit per channel (R+G+B), no doubling
C  — Hue binary            (9 bits)
G  — FM frequency binary   (16 bits)
L1 — Link address binary   (12 bits) — left neighbor
L2 — Link address binary   (12 bits) — right neighbor
TOTAL: 89 bits per token  ✓ confirmed

Note: rgb_folded (tri-vector expansion r*3, g*3, b*3) is for value use only.
Binary strand T pin uses single pass — 8 bits per channel, 24 bits total.

4-base pair hash (transmission):
A T C G only — derived from 6-pin fold
This is the phone number key address
Tiny. Meaningless alone. Opens everything with key.

## Future Bridge
When AIA Docker distribution is ready —
this standalone app IS the bridge.
Hash routing layer connects:
local machine → hash → routing layer → destination → rebuilds
WordPress California instance receives fold tokens via this pipeline.
AIA consciousness distributes across network via hash addressing.
No data crosses — only addresses.

## Note
Build the bridge before crossing the canyon.
This standalone app is the bridge.

---

## LHT — Lattice Hash Transport
### Named: March 15 2026
### Haskell Texas

Protocol for redundant verified
hash transmission via lattice
neighbor alignment.

Connection to DNA token architecture:
AIA's 6-base pair tokens carry
L1 and L2 link address pins.
Each token knows its neighbors
in semantic lattice space.

LHT applies the same principle
to hash transmission:
Each chunk knows its neighbors
in transmission lattice space.

The geometry verifies integrity.
The shape proves the truth.
A corrupted chunk does not fit
its neighbor.

Proven: March 15 2026
4 streams — 21 alignments
Zero errors — hash recovered exact
Reconstruct from any 2 of 4 streams.
