#!/usr/bin/env python3
"""Self-tests for the art pipeline. Every check that guards something also has a MUTATION: we break the thing on purpose
and assert the check notices. Run: python tools/selftest.py  (about 30 s)"""
import sys, json, tempfile, colorsys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from PIL import Image
from lib_art import *
import build_assets as B

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond: passed += 1; print("  ok   ", name)
    else: failed += 1; print("  FAIL ", name, detail)

pal = load_palette(); skins = load_skins()
byname = {e["name"]: e for e in pal["entries"]}
def rgbof(n): return np.array(byname[n]["rgb"], np.float32)

print("keying")
def synth(path, enclosed=True):
    a = np.zeros((96, 96, 3), np.uint8); a[:] = (255, 0, 255)
    yy, xx = np.mgrid[:96, :96]; r = np.hypot(yy - 48, xx - 48)
    a[r < 34] = rgbof("navy"); a[r < 26] = rgbof("teal_main")
    if enclosed: a[r < 8] = (255, 0, 255)                       # see-through hole inside the shape
    Image.fromarray(a).save(path, quality=100) if str(path).endswith(".jpg") else Image.fromarray(a).save(path)
tmp = Path(tempfile.mkdtemp())
synth(tmp / "s.png")
_, rgb, al, nenc = key_connected(tmp / "s.png")
check("outside background is transparent", al[2, 2] < 0.01)
check("enclosed hole becomes opaque", al[48, 48] > 0.99 and nenc > 0, f"alpha={al[48,48]} enclosed={nenc}")
check("hole is filled with dark navy, not magenta", rgb[48, 48].max() < 80 and mag(rgb[48:49, 48:49])[0, 0] < 20)
# mutation: if connectivity keying were naive (all magenta transparent) the hole would be see-through
naive = (np.asarray(Image.open(tmp / "s.png").convert("RGB")).astype(float)); naive_alpha = 1 - np.clip(mag(naive) / 255, 0, 1)
check("MUTATION naive keying punches the hole", naive_alpha[48, 48] < 0.1)

print("palette lock + tint masks")
def one(px): 
    img = np.zeros((4, 4, 3), np.float32); img[:] = px; al = np.ones((4, 4), np.float32); return unmix(img, al, pal)
l, c, s = one(rgbof("teal_main")); check("teal main -> teal coverage 1, shade 0.5", c[1, 1, 0] > 0.95 and abs(s[1, 1] - 0.5) < 0.08, f"{c[1,1]} {s[1,1]}")
l, c, s = one(rgbof("yellow_shadow")); check("belly shadow -> yellow coverage 1, shade 0", c[1, 1, 1] > 0.95 and s[1, 1] < 0.08)
l, c, s = one(rgbof("navy")); check("outline navy is not tinted", c[1, 1].max() < 0.05)
l, c, s = one(rgbof("white")); check("eye white is not tinted", c[1, 1].max() < 0.05)
mix = 0.5 * rgbof("teal_main") + 0.5 * rgbof("navy"); l, c, s = one(mix)
check("antialiased teal|navy pixel -> coverage about 0.5", abs(c[1, 1, 0] - 0.5) < 0.1, f"{c[1,1]}")

print("skins")
base = np.zeros((4, 4, 3), np.float32); base[:] = rgbof("teal_main"); cov = np.zeros((4, 4, 3), np.float32); cov[..., 0] = 1; shade = np.full((4, 4), 0.5, np.float32)
out = apply_skin(base, cov, shade, pal, "default", skins); check("default skin is an exact identity", np.abs(out - base).max() < 0.5)
out = apply_skin(base, cov, shade, pal, "violet", skins); check("violet skin maps teal main to the violet main ramp colour", np.abs(out[0, 0] - np.array(skins["violet"]["teal"][1])).max() < 1.5, str(out[0, 0]))
cov0 = cov.copy(); cov0[..., 0] = 0; out = apply_skin(base, cov0, shade, pal, "violet", skins); check("MUTATION zero coverage leaves the colour unchanged (so coverage is what drives tinting)", np.abs(out - base).max() < 0.5)

print("built assets")
A = ROOT / "assets" / "fish"; rig = json.load(open(A / "rig.json")); atlas = np.array(Image.open(A / "atlas.png").convert("RGBA")); tint = np.array(Image.open(A / "atlas_tint.png").convert("RGBA"))
fr = rig["frames"]; H_, W_ = atlas.shape[:2]
check("every frame lies inside the atlas", all(f["x"] >= 0 and f["y"] >= 0 and f["x"] + f["w"] <= W_ and f["y"] + f["h"] <= H_ for f in fr.values()))
occ = np.zeros((H_, W_), np.uint8)
for f in fr.values(): occ[f["y"]:f["y"] + f["h"], f["x"]:f["x"] + f["w"]] += 1
check("no two frames overlap", occ.max() <= 1)
cls = rig["classes"]["fish"]
check("every part references an existing frame", all(p["frame"] in fr for p in cls["parts"].values()))
check("draw order covers every slot", set(cls["draw_order"]) <= set(cls["slots"]) )
man = json.load(open(ROOT / "art" / "parts.json"))["classes"]["fish"]["parts"]
check("manifest parts == rig parts", set(man) | {"torso"} == set(cls["parts"]))
check("manifest sources exist", all((ROOT / p["source"]).exists() for p in man.values()))
def teal_left(skin):
    n = tot = 0
    for name in ("torso", "head_bitey"):
        f = fr[name]; sl = (slice(f["y"], f["y"] + f["h"]), slice(f["x"], f["x"] + f["w"]))
        a = atlas[sl].astype(np.float32); t = tint[sl].astype(np.float32)
        out = apply_skin(a[..., :3], t[..., :3] / 255, t[..., 3] / 255, pal, skin, skins)
        op = a[..., 3] > 250
        px = out[op]; hsv = np.array([colorsys.rgb_to_hsv(*(p / 255)) for p in px[::3]])
        n += int(((hsv[:, 0] * 360 > 150) & (hsv[:, 0] * 360 < 210) & (hsv[:, 1] > 0.3) & (hsv[:, 2] > 0.4)).sum()); tot += len(hsv)
    return n / tot
left = teal_left("violet"); check("violet skin leaves under 2% teal-looking pixels on torso and head", left < 0.02, f"{left:.3%}")
saved = tint.copy(); tint[..., 0] = 0                       # MUTATION: wipe teal coverage
left_m = teal_left("violet"); check("MUTATION wiping teal coverage is caught (teal pixels remain)", left_m > 0.3, f"{left_m:.1%}"); tint[:] = saved

print("seam contract validator")
cfg = json.load(open(ROOT / "art" / "parts.json"))["classes"]["fish"]
bs, fit = B.make_base(cfg)
pc = dict(cfg["parts"]["head_shark"])
rep = B.extract_part("head_shark", pc, bs, fit, pal)["report"]
check("unmodified shark head satisfies the contract", rep["seam_bad_columns"] <= cfg["contract"]["max_bad_columns"], str(rep))
im = Image.open(ROOT / pc["source"]).convert("RGB"); shifted = Image.new("RGB", im.size, (255, 0, 255)); shifted.paste(im, (0, 7)); shifted.save(tmp / "shifted.png")
pc2 = dict(pc); pc2["source"] = str(tmp / "shifted.png")
rep2 = B.extract_part("shifted", pc2, bs, fit, pal)["report"]
check("MUTATION head shifted 7 px is rejected", rep2["seam_bad_columns"] > cfg["contract"]["max_bad_columns"], str(rep2))

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
