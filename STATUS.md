# Status

Updated: 2026-10-26, session 2 (asset pipeline built). Sessions are run by hand in a free-tier Claude chat; the chat cannot push.

## 1. Playable / runnable now
No game yet. Runnable: the art pipeline.
- `python tools/build_assets.py` builds `assets/fish/` (atlas.png, atlas_tint.png, rig.json) from `art/parts.json`; ~100 s.
- `python tools/preview_skins.py` writes `docs/skin_preview.png` (5 heads x 5 skins x tail swing, rendered from the atlas).
- `python tools/selftest.py` runs 22 checks (~30 s).
First playable target: the sea-level vertical slice (`docs/TASKS.md`, S1-S17).

## 2. Verified, and how
- `selftest.py`: 22/22 pass. Includes keying of enclosed holes, palette lock and tint coverage on synthetic pixels, skin identity and mapping, atlas integrity
  (frames inside, no overlaps, manifest == rig), a violet-skin completeness check (< 2% teal-looking pixels left on torso + head), and the seam validator.
  Each guard has a MUTATION check (naive keying, zero coverage, wiped teal coverage, a head shifted 7 px) that must be noticed; all were.
- Visual checks of the atlas-rendered preview (`docs/skin_preview.png`): five heads and five skins, tail swing; head/torso seam invisible after a fix
  (shared-grid downscale, colour bleed, 6 px head overlap).
- Earlier: resolution test (`docs/res_test.png`: 960x540 reads well, 480x270 is muddy), four heads on the base torso (`docs/head_gallery.png`).

## 3. NOT verified
- Anything in a browser/engine: no game code or shader exists; the recolour formula is only checked by the Python reference.
- A second class (amphibian etc.), more than one variant per fin/tail/horn, and generator drift over many edits.
- Original-game numbers in `docs/RESEARCH.md` (from web sources, not cross-checked).
- How the atlas looks at 4K (atlas is x0.34 of the 1024 canvas, i.e. a 2x asset for a 960x540 game).

## 4. Known issues
- `head_jaw1`: Gemini added a tail behind the seam (26k px); ignored by the build but flagged as a warning.
- Tail rotation beyond about +/-8 degrees (dorsal about +/-3) shows hidden-root slivers (S3f).
- About 3% of pixels (eye glints, odd antialiasing) match no palette model and stay untinted; visible as a few stray teal pixels in the pupil under strong skins.
- The carp head has a small derpy eye; the shark's teeth are white while others are cream; horn anchors for all heads except base are guesses (S3k).
- Lower-jaw belly shading steps at the seam on some heads (design of the head, not a bug).
- Build takes ~10 s per image (S3j).

## 5. Next steps (priority order)
1. Scaffold (S1) and an in-engine rig prototype at 960x540 (S4): load `assets/fish`, draw parts by `draw_order`, write the skin shader, swim/sway, swap heads and skins from keys. This is the first real browser test of the pipeline.
2. Gemini batch (human): second shapes for tail, side fin, dorsal fin and horn (in-place edits, no colour changes, "no shadow under the part").
3. Anchor editor (S5) and tail-bend decision (S3f).
4. Swim/bite controls, one enemy, evolution menu (S6-S11).

## 6. Needs the human
- Gemini generations for the next art batch (prompts in `docs/ART_STYLE.md`).
- Confirm or change the proposed decisions in `docs/PLAN.md` (engine, resolution, part system).
- Delete the files superseded by this update (list in the hand-over message): `art/rig/`, `tools/extract_parts.py`, `tools/preview_rig.py`, `tools/head_tint_test.py`, `tools/resolution_test.py`.

## Decisions worth remembering
- Chibi, cutesy, original art only; Gemini is the art generator; parts are in-place edits of a base body, extracted per `art/parts.json`.
- Resolution 960x540 internal; atlas at x0.34 of the 1024 canvas; linear filtering.
- Head slot = everything in front of a vertical seam just in front of the gill line (owner's idea). Torso + head share one skin; fins/horn may use another.
- Colour variety is runtime recolour (palette ramps + tint masks), never extra art. New colours enter via `art/palette.json` entries.
- Every guard in the pipeline gets a mutation check (break it on purpose, watch the test fail).
- The original ROM, if used at all, is a private reference for numbers and behaviour only; nothing from it goes into the repo, and the ROM is never committed.

## Session log
- Session 1 (2026-10-23): research of the original game; design decisions; generator test (Gemini chosen); in-place part workflow; head-slot idea; first head edits (jaw 1, shark, bitey, carp); starter repo; independent review accepted (resolution 960x540, manifest, validator, atlas).
- Session 2 (2026-10-26): manifest-driven build, palette lock + tint masks + skins, near-vertical seam, atlas packer, validator, self-tests with mutation checks, skin preview.
