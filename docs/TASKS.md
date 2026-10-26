# Tasks

Effort scale: **Low** = mechanical/boilerplate - **Medium** = standard implementation -
**High** = tricky systems/edge cases - **Max** = hardest, design-heavy. "(volume)" = effort is quantity, not difficulty.

## Vertical slice (current focus)
- [ ] S1  Scaffold (Vite+TS, loop, 960x540 internal resolution with linear filtering, input) - Medium
- [x] S2  Style test: generators compared, Gemini chosen, style reference locked - Low
- [x] S3  Art pipeline - High  (manifest-driven build, validator, palette lock, tint masks, atlas; `python tools/build_assets.py`)
  - [x] S3a Parts manifest `art/parts.json` (slot, source, mode, layer, anchors); variants are just more entries - Medium
  - [x] S3b Contract validator: silhouette at the seam, extracted area, unrequested additions (warning) - High
        (still open: QA contact sheet of all parts; PNG input preferred but JPG is fine)
  - [x] S3c Atlas packer: shared-grid downscale (x0.34), trim, bleed, pack; outputs `assets/fish/` (committed, ~260 KB) - Medium
  - [x] S3d Head slot: torso + swappable heads cut at a vertical seam in front of the gill line (head overlaps 6 px) - Medium
  - [x] S3e Skins: palette ramps + tint masks (`art/palette.json`, `art/skins.json`), reference recolour in `tools/lib_art.py` - Medium
        (engine shader still to write: `out = rgb + sum_f cov_f * (skinRamp_f(shade) - defaultRamp_f(shade))`)
  - [ ] S3f Tail bend: rotation is clean to about +/-8 degrees, hidden roots poke out at +/-10; decide mesh bend vs rotation limits - Medium
  - [x] S3g Keying by connectivity (enclosed magenta -> dark navy) - Medium
  - [x] S3h Palette lock (also yields the tint masks) - Medium
  - [x] S3i Near-vertical seam - Medium
  - [ ] S3j Build speed: about 10 s per image (palette unmixing); cache by source hash - Low
  - [ ] S3k Per-head anchors for the horn are a guess (carp especially); set them in the anchor editor (S5) - Low
  - [x] Self-tests with mutation checks: `python tools/selftest.py` (22 checks)
- [~] S4  Rig/compositor - Max  (atlas + `rig.json` with frames, pivots, draw order and anchors done; in-engine rig, skin shader and procedural animation to do)
- [ ] S5  Anchor editor tool (drag parts, set pivots, preview poses) - High
- [ ] S6  Swim physics, camera, tilemap loader - High
- [ ] S7  Hitboxes, bite, horn ram, tail slap, knockback - High
- [ ] S8  Enemy AI behaviours (drift, chase, patrol, ambush) - High
- [ ] S9  Drops, eating, EP/HP economy, death and revive - Medium
- [ ] S10 Stat model + part data (fish class) - High
- [ ] S11 Evolution menu with preview and stat diff - High
- [ ] S12 Level layout in Tiled, hint crystal, checkpoint - Medium
- [ ] S13 Boss with 2-3 attack patterns - High
- [ ] S14 HUD, title, pause, Gaia dialogue box - Medium
- [ ] S15 SFX + one music loop - Medium
- [ ] S16 Balance pass: boss beatable by two different builds - High
- [ ] S17 Tests + Pages deploy - Medium

### Slice art checklist
- [x] Base body, tail, dorsal fin, side fin, horn (one variant each)
- [x] Heads: base smile, toothy (jaw 1), shark, bitey, carp - all pass the seam contract (extraction into the pipeline pending S3d, S3g-i)
- [ ] Second shapes for tail, side fin, dorsal fin and horn so the evolution menu has real choices
- [ ] Per-head anchors (horn mount) for every head variant
- [ ] Enemies: jellyfish, prey fish, seafloor crawler, pufferfish-style hazard, 1 more
- [ ] Boss (+ jaw/tail as separate pieces if possible)
- [ ] Tileset, 3 parallax layers, bubbles/hit sparks
- [ ] UI: HP/EP bars, meat/crystal icons, evolution menu frame, Gaia portrait

## Full game (after the slice)
**M0 Foundations**: repo/CI/deploy (Low), loop+scenes (Medium), scaling (Low), input + rebinding (Medium),
asset manifest/atlas (Medium), data schemas + validation (Medium), debug overlay (Low)

**M1 Core**: tilemap/collision/slopes (High), player controller land+swim (High), camera/parallax (Medium),
hitbox/hurtbox/i-frames (High), attack set bite/stomp/kick/strike/horn/tail (High), enemy AI library (High),
drops/eating (Medium), HUD (Low), death/revive (Medium)

**M2 Evolution**: stat model (High), part database for all five classes (High), evolution menu (High),
class-change event + EP rules (High), crystals + hidden forms incl. Human (Medium), rig/compositor for every class (Max),
animation states per class (High), transform animation (Low), headless balance simulator (High)

**M3 World**: overworld map (Medium), stage flow + revisit (Medium), dialogue/cutscenes (Medium),
intro/chapter intros/ending/credits (Medium), save/load (Medium), title/options/pause (Low)

**M4 Content (x5 chapters)**: stage layouts (Medium), enemy rosters (High), mid-bosses and chapter bosses (High),
final boss (Max), hazards (Medium), crystal/secret placement (Low), difficulty tuning (High)

**M5 Art**: art direction per class (Medium), tilesets/backgrounds (Medium, volume), player part sprites for 5 classes
(Max, volume), enemy/boss sprites (Max, volume), UI/font/VFX (Medium)

**M6 Audio**: audio engine (Medium), SFX set (Medium), music for menu/chapters/boss/ending (High)

**M7 Polish**: touch controls (Medium), performance (Medium), accessibility (Low), unit tests (Medium),
Playwright smoke test (Medium), docs (Low), release pipeline (Low)
