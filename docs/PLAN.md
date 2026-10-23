# Design plan

## Goal
A browser remake of E.V.O.: Search for Eden. Faithful in structure (five eras, eight body slots, EVO-point
economy, evolving mid-level), modernized in feel (fair hitboxes, checkpoints, clearer evolution menu).

## Decisions
**Decided (by the project owner)**
- Art style: chibi, cutesy. Original art only.
- First milestone: vertical slice of ONE sea level from the first era (fish form).
- Art is generated with **Gemini**, following the style bible in `docs/ART_STYLE.md` (chosen for look and generous free usage).
- Repo is private; Claude reads it through the Claude Project GitHub integration (see `docs/WORKFLOW.md`).

**Proposed (not yet confirmed - change freely)**
| Topic | Proposal | Why / alternative |
|---|---|---|
| Fidelity | Faithful structure, modern feel (tight hitboxes, checkpoints, warn when an evolution removes healing) | The original's collision and grind are known weak points |
| Perspective | Single-plane side-scroller | Matches the original; simpler level design than depth lanes |
| Engine | TypeScript + Vite + Phaser 3 | Tiled import, audio, input, scaling for free. Alternative: custom Canvas2D |
| Resolution | 480x270 internal, integer scaling, nearest-neighbour | AI art cannot hold a strict SNES pixel grid; 16:9 is friendlier |
| Body rendering | Skeleton rig: base body + part sprites on pivots, animated procedurally in-engine | No frame-by-frame art needed; ~150-250 part sprites for the full game |
| Data | Parts, enemies, stages, bosses as validated JSON | Balance without touching code |
| Level authoring | Tiled (JSON export) | Standard |
| Audio | Web Audio; synthesized SFX; original chiptune music | |
| Saves | localStorage, 3 slots, versioned | |
| Death | Return to map, EP halved, no game over (as the original) | |
| Hosting/tests | GitHub Pages, Vitest, Playwright smoke test | |

## Vertical slice scope (about 3 minutes of play)
Shallows tutorial (prey fish, eating) -> kelp section (jellyfish) -> seafloor dip (hint crystal) ->
pre-boss evolve prompt -> boss arena (one small cute boss; the shark is saved for the full game).

Assets: fish base + about 21 part sprites (jaws x4, horn x4, body x3, fins x3, dorsal x3, tail x4),
5 enemy/prey types, 1 boss, tileset, 3 parallax layers, UI icons, Gaia portrait.

**Slice is done when:** swimming and biting feel good; evolving visibly changes the fish and its stats;
the boss is beatable with at least two different builds; the art pipeline works prompt -> sprite repeatably.

## Art pipeline (proven so far)
1. Generate a hero + a naked base body (flat #FF00FF background).
2. Ask Gemini to ADD one part to the base body *in the same canvas* (in-place edit).
3. `tools/extract_parts.py` diffs the edit against the base body, keys out the magenta, and saves the part as a
   full-canvas RGBA layer plus a pivot in `art/rig/rig.json`.
4. Because parts are drawn in place, scale and outline weight match the body by construction.

## Risks
- Rig + procedural animation is the riskiest system: prototype it in-engine first.
- Part consistency across many variants (style drift): one generator, fresh chat per batch, same references.
- Outline weight must stay consistent; never scale parts independently.
- Content volume (levels, enemies, bosses, music) dwarfs the slice.
