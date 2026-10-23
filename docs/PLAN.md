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
| Resolution | **960x540** internal (16:9), linear filtering, sprites pre-downscaled at pack time to their display size, 2x to 1080p | Revised after a test (`docs/res_test.png`): at 480x270 the ~2.5% outline shrinks to ~1.6 px and eye/fin detail turns muddy; this art is smooth, not pixel art |
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

## Part system (how variants and slots work)
- **One naked base body per class** (fish, amphibian, reptile, bird, mammal); a new silhouette appears only at a class change.
  Every part of that class is an in-place edit of that class's base body.
- **Body variants are skins, not new silhouettes**: tint/pattern/overlay (scales, shell plates) on the fixed silhouette, plus a
  uniform size scale for "bigger/smaller body". Uniform scaling keeps outline ratios. This keeps every attachment point valid.
- **Jaws**: the base body is regenerated *without* the mouth line (eye and gill line stay); the default smile becomes jaw variant 01,
  so teeth/beaks are drawn into an empty snout instead of over an existing mouth.
- **Manifest, not hard-coded lists**: `art/parts.json` lists slot, variant, source edit, layer (behind/front) and any extraction overrides.
- **Repo health**: commit only trimmed, downscaled atlas output; full-canvas 1024x1024 layers are build artefacts
  (~4 MB each in GPU memory untrimmed, ~280 KB each on disk, which does not scale to 150-250 parts).

## Art pipeline (proven so far)
1. Generate a hero + a naked base body (flat #FF00FF background).
2. Ask Gemini to ADD one part to the base body *in the same canvas* (in-place edit).
3. `tools/extract_parts.py` diffs the edit against the base body, keys out the magenta, and saves the part as a
   full-canvas RGBA layer plus a pivot in `art/rig/rig.json`.
4. Because parts are drawn in place, scale and outline weight match the body by construction.

## Risks (updated after an independent review)
- Extraction depends on Gemini leaving the body pixel-identical in every edit: needs a validator (drift check) before more parts.
- Hand-tuned thresholds (horn, side fin) will not scale to hundreds of parts without a manifest and a QA contact sheet.
- Rotation seams appear beyond the safe limits (tail ~12 degrees, dorsal ~4); the earlier preview deliberately pushed past them.
- Rig + procedural animation is the riskiest system: prototype it in-engine first.
- Part consistency across many variants (style drift): one generator, fresh chat per batch, same references.
- Outline weight must stay consistent; never scale parts independently.
- Content volume (levels, enemies, bosses, music) dwarfs the slice.
