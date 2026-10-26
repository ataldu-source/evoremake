#!/usr/bin/env python3
"""Reference renderer for the built atlas: composes the rig and applies skins exactly as the game shader should.
Writes docs/skin_preview.png.  Usage: python tools/preview_skins.py"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_art import *
from PIL import ImageDraw

A = ROOT / "assets" / "fish"
rig = json.load(open(A / "rig.json")); pal = load_palette(); skins = load_skins()
atlas = np.asarray(Image.open(A / "atlas.png").convert("RGBA")); tint = np.asarray(Image.open(A / "atlas_tint.png").convert("RGBA"))
S = rig["atlas"]["scale"]; CAN = round(1024 * S)
cls = rig["classes"]["fish"]

def frame_arrays(name):
    f = rig["frames"][name]; sl = (slice(f["y"], f["y"] + f["h"]), slice(f["x"], f["x"] + f["w"]))
    return atlas[sl].astype(np.float32), tint[sl].astype(np.float32), f

def layer(name, skin_body, skin_fins, rot=0.0):
    a, t, f = frame_arrays(name)
    rgb = a[..., :3]; al = a[..., 3] / 255.0; cov = t[..., :3] / 255.0; shade = t[..., 3] / 255.0
    group = cls["parts"][name]["skin_group"]; slot = cls["parts"][name]["slot"]
    if slot in ("torso", "head"):
        out = apply_skin(rgb, cov, shade, pal, skin_body, skins)
    elif group == "teal+coral":
        out = apply_skin(rgb, cov, shade, pal, skin_body, skins, only=["teal"]); out = apply_skin(out, cov, shade, pal, skin_fins, skins, only=["coral"]) if False else out
        o2 = apply_skin(rgb, cov, shade, pal, skin_fins, skins, only=["coral", "yellow"]); out = out + (o2 - rgb)
    else:
        out = apply_skin(rgb, cov, shade, pal, skin_fins, skins)
    img = Image.fromarray(np.dstack([np.clip(out, 0, 255), al * 255]).astype(np.uint8), "RGBA")
    canvas = Image.new("RGBA", (CAN, CAN), (0, 0, 0, 0)); canvas.alpha_composite(img, (round(f["ox"]), round(f["oy"])))
    if rot:
        canvas = canvas.rotate(rot, center=tuple(f["pivot"]), resample=Image.BICUBIC)
    return canvas

def fish(head, skin_body="default", skin_fins=None, horn=False, tail_rot=0.0, dorsal_rot=0.0, bg=(30, 90, 140)):
    skin_fins = skin_fins or skin_body
    c = Image.new("RGBA", (CAN, CAN), bg + (255,))
    for slot in cls["draw_order"]:
        if slot == "horn" and not horn: continue
        name = {"torso": "torso", "head": head, "tail": "tail_01", "dorsal": "dorsal_01", "sidefin": "sidefin_01", "horn": "horn_01"}[slot]
        c.alpha_composite(layer(name, skin_body, skin_fins, tail_rot if slot == "tail" else dorsal_rot if slot == "dorsal" else 0))
    return c.crop((int(CAN * .05), int(CAN * .22), int(CAN * .98), int(CAN * .74)))

def main():
    heads = ["head_base", "head_jaw1", "head_shark", "head_bitey", "head_carp"]
    rows = [[(h, "default", None, False, 0, 0) for h in heads],
            [("head_shark", "violet", None, False, 0, 0), ("head_bitey", "reef", "rose", False, 0, 0), ("head_carp", "lime", None, False, 0, 0),
             ("head_jaw1", "rose", "lime", True, 0, 0), ("head_base", "default", "violet", True, 0, 0)],
            [("head_bitey", "violet", None, True, a, d) for a, d in [(-10, -3), (-5, 0), (0, 0), (5, 0), (10, 3)]]]
    probe = fish("head_base"); w, h = probe.size
    sheet = Image.new("RGB", (w * 5, (h + 18) * 3), (240, 240, 240)); d = ImageDraw.Draw(sheet)
    for r, row in enumerate(rows):
        for c, (hd, sb, sf, horn, tr, dr) in enumerate(row):
            im = fish(hd, sb, sf, horn, tr, dr); sheet.paste(im.convert("RGB"), (c * w, r * (h + 18) + 18))
            d.text((c * w + 6, r * (h + 18) + 3), f"{hd} | body {sb} | fins {sf or sb}" + (f" | tail {tr:+d}" if r == 2 else ""), fill=(0, 0, 0))
    out = ROOT / "docs" / "skin_preview.png"; sheet.save(out); print("wrote", out.relative_to(ROOT), sheet.size)

if __name__ == "__main__":
    main()
