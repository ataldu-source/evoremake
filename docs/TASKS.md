# Tasks

Effort scale: **Low** = mechanical/boilerplate - **Medium** = standard implementation -
**High** = tricky systems/edge cases - **Max** = hardest, design-heavy. "(volume)" = effort is quantity, not difficulty.

## Vertical slice (current focus)
- [ ] S1  Scaffold (Vite+TS, loop, 480x270 scaling, input) - Medium
- [x] S2  Style test: generators compared, Gemini chosen, style reference locked - Low
- [~] S3  Art pipeline + validator - High  (extraction and preview scripts done; validator, atlas packer, outline check still to do)
- [~] S4  Rig/compositor - Max  (static rig data + pivots done in `art/rig`; in-engine rig and procedural animation to do)
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
- [ ] Jaws (teeth) - at least 3 more variants of tail/horn/fin/jaw so the evolution menu has real choices
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
