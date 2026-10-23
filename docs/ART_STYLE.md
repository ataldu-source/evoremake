# Art style bible and generation workflow

Generator: **Gemini** (best character and parts consistency; generous free usage). ChatGPT is a good literal fallback
(PNG output, flat colours) but has a daily cap; Grok ignored the background colour and added a drop shadow.

## Look
Chibi and cute: big head, big glossy eyes with highlights, thick uniform dark-navy outline (#1B2A49), flat cel shading
with one soft shadow tone, no gradients, texture noise, text or watermarks. Strict side view, facing right.
Palette (player fish): body teal #4FD1C5, shadow #2C9FA6, belly pastel yellow #FFE7A3, accent coral #FF8A5B, outline #1B2A49.
Parts use coral and cream, **not teal**, so they stand out against the body.

## Canvas rules
- 1024x1024 square, subject fully visible with margin on all sides.
- Background: one flat solid **#FF00FF** magenta. No shadow, glow, halo or ground line. No magenta/pink/purple on the subject.
- Outline weight of the base body is about 2.5% of its length. Never scale a part on its own: it changes the outline weight.
- Ask for PNG if the tool offers it; JPG also keys cleanly.

## Prompts
**Style block** (top of every prompt)
```
Cute chibi 2D game sprite illustration (not pixel art, not 3D), clean thick dark-navy outline of uniform weight,
flat cel shading with ONE soft shadow tone, no gradients, no texture noise, no glow, no text, no watermark.
Soft saturated ocean palette, big glossy eyes with a white highlight, simple rounded shapes. Strict side view in
profile facing right. Single subject centered on a flat solid #FF00FF background, no shadow, no ground line,
fully visible with margin on all sides. Output exactly one image, square aspect ratio.
```
**Hero (style lock)**: style block + tiny minnow-like fish hero with small tail, side fin and dorsal fin, no horn, mouth closed.
**Naked body**: attach the hero; "draw the SAME fish with NO tail, NO side fin, NO dorsal fin, NO horn".
**Part, in place** (attach `art/raw/body_base.jpg`; change the bracketed part)
```
Attached is my game fish body. Edit the image by ADDING a [forked tail in coral and cream, tucked behind the rear
point of the body]. Do NOT change the body in any way: same position, size, colors and outline thickness. The new
part must have the same navy outline weight as the body and the same flat cel shading, and must NOT be teal. Keep the
flat #FF00FF magenta background, no shadow under the part, no glow. Output the full image at the same square canvas size.
```
Parts used so far: tail (behind, rear), dorsal fin (behind, top), side fin (in front, near the gill line, no shadow),
horn (spiral, collar at top front of head, pointing right).

**Head variant** (attach `art/raw/body_base.jpg`; first try: toothy jaws)
```
Attached is my game fish. Edit it by REPLACING the head: everything in FRONT of the curved gill line gets a new head with
[sharp visible teeth and a slightly larger lower jaw]. Everything behind and including the gill line must stay EXACTLY
unchanged: do NOT add a tail, fins or anything else. The new head must meet the top and belly outlines at the same two points
and be the same height at the gill line. Same teal and yellow colours, same navy outline weight, same chibi style.
The inside of the mouth must be SOLID DARK NAVY, fully enclosed by the outline, never see-through, never pink or purple.
Flat #FF00FF background, no shadow. Same canvas, same position. One image, square.
```

## Per-asset QA checklist
Faces right - whole sprite visible - magenta flat with no halo/shadow - outline weight matches the body -
colours inside the palette - body unchanged between base and edit (same position on the canvas).

## Workflow and tips
1. Fresh chat per batch (all tails in one session, all fins in another); attach the same references each time.
2. Generate 3-4 attempts per part and pick the best; extra generations are cheap.
3. Save the approved edit as `art/raw/edit_<part>.jpg` (add `_02`, `_03` for variants), note the prompt in the commit message.
4. `python tools/extract_parts.py`, then `python tools/preview_rig.py`, and look at `art/rig/rig_preview.png`.

## Lessons learned
- Parts generated on their own come out with different outline weights and scales; in-place edits fix that.
- Gemini may add a soft drop shadow under parts (side fin): the extractor drops it, but ask for "no shadow".
- Gemini redrew a small teal socket around the horn base; the extractor keeps it as part of the horn.
- Rotation limits for clean results with the hidden roots: tail about +/-12 degrees, dorsal about +/-4 degrees.
- Head edit 1 (toothy jaws) worked: the silhouette at the seam matched the base exactly and the head swaps onto the base torso
  (`docs/head_swap_test.png`). Gemini also added an unrequested tail (harmless: everything behind the seam is discarded, and the
  prompt now says not to). It painted part of the mouth interior in the background magenta, which the keyer treated as see-through;
  fixed in the pipeline (see TASKS S3g) and by asking for a solid dark mouth interior.
- Gemini re-renders flat colours slightly differently per image (belly yellow blue-channel 132 vs 124), which shows as a faint seam
  line; the pipeline snaps colours to the base palette (S3h).
- Heads 2-4 (shark, bitey, carp): none added a tail; all kept the seam silhouette. Bitey is the cleanest (solid dark mouth, cream teeth).
  Variation to watch: eye size/style (the carp's small eye breaks the "big glossy eye" rule), teeth colour (white vs cream), and
  see-through gaps between teeth. Add to head prompts: "keep the same big glossy eye" and "teeth cream (#F5E7B8)".
