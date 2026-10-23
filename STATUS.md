# Status

Updated: 2026-10-23, session 1 (planning + art-pipeline prototype). Sessions are run by hand in a free-tier Claude chat; the chat cannot push.

## 1. Playable / runnable now
No game yet. Runnable: the art pipeline (`python tools/extract_parts.py`, `python tools/preview_rig.py`, `python tools/resolution_test.py`).
First playable target: the sea-level vertical slice (see `docs/TASKS.md`, S1-S17).

## 2. Verified, and how
- The pipeline rebuilds the committed rig parts and `rig.json` pixel for pixel from `art/raw/` (compared after a clean re-run; an independent reviewer repeated it).
- Keying of magenta backgrounds is clean on JPG and PNG, no halo on dark/light/white backgrounds (viewed).
- Resolution test (`docs/res_test.png`): the art reads clearly at 960x540 and muddy at 480x270.

## 3. NOT verified
- Any in-engine rendering, rig animation or game code (none exists).
- Part consistency over many variants and a second class (only one variant per slot on the fish).
- That Gemini keeps the body pixel-identical in every edit (no validator yet; checked by eye on 4 edits).
- Original-game numbers in `docs/RESEARCH.md` (taken from web sources, not cross-checked).

## 4. Known issues
- Rotation seams beyond tail ~12 / dorsal ~4 degrees (hidden roots poke out).
- Extractor has hand-tuned thresholds for horn and side fin; part lists are hard-coded; no variants yet.
- Base body has the mouth baked in, so jaws would be drawn over it (plan: mouthless base v2).
- Full-canvas 1024x1024 part layers are committed; they will not scale (plan: trimmed atlas).

## 5. Next steps (priority order)
1. Parts manifest + body-drift validator + atlas packer (S3a-c).
2. Mouthless base body and jaw slot; a second variant for tail, horn, fin (art, by the human with Gemini).
3. Scaffold (S1) and an in-engine rig prototype at 960x540 (S4): swim, sway, swap parts.
4. Swim/bite controls and one enemy (S6-S8), then evolution menu (S10-S11).

## 6. Needs the human
- Gemini generations for the next art batch (prompts in `docs/ART_STYLE.md`).
- Confirm or change the proposed decisions in `docs/PLAN.md` (engine, resolution, part system).
- Optional: the original ROM is available to the human; see the note below on how it may be used.

## Decisions worth remembering
- Chibi, cutesy, original art only; Gemini is the art generator; parts are generated as in-place edits of a base body and extracted by diffing.
- Resolution 960x540 with pre-downscaled sprites (revised from 480x270 after the test).
- Body variants are skins on a fixed silhouette; one base body per class; jaws are their own slot over a mouthless base.
- The original ROM, if used at all, is a private reference for numbers and behaviour. No sprites, music, maps or text from it go into the repo, and the ROM itself is never committed.

## Session log
- Session 1 (2026-10-23): research of the original game; design decisions; art style test across three generators (Gemini chosen); in-place part workflow and extractor; starter repo; independent review accepted, resolution revised, part-system rules written.
