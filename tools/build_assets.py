#!/usr/bin/env python3
"""Build game-ready assets from art/parts.json.

  python tools/build_assets.py            # build + validate; exits 1 if a part breaks the contract
  python tools/build_assets.py --check    # validate only, write nothing

Pipeline per part: key (border-connected magenta) -> palette lock + tint masks -> extract the part (diff / loop / seam)
-> validate against the base body -> trim -> downscale to atlas_scale -> pack.
Outputs (committed, small): assets/fish/atlas.png, atlas_tint.png, rig.json.   QA: build/contact_sheet.png, build/report.json
"""
import sys, json, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from lib_art import *

def sx_grid(fit, H, W):
    return seam_x(fit, np.arange(H))[:, None], np.arange(W)[None, :]

def make_base(cfg):
    raw, rgb, alpha, _ = key_connected(ROOT / cfg["base"])
    body = ndi.binary_fill_holes(alpha > 0.5)
    base = {"raw": raw, "rgb": rgb, "alpha": alpha, "mask": body, "seam_cfg": cfg["seam"], "contract": cfg["contract"]}
    return base, fit_seam(rgb, alpha, cfg["seam"])

def extract_part(name, cfg, base, fit, pal):
    """Returns dict(rgb, cov, shade, alpha, pivot, report) in full-canvas coordinates."""
    raw, rgb, alpha, nenc = key_connected(ROOT / cfg["source"])
    locked, cov, shade = unmix(rgb, alpha, pal)
    H, W = alpha.shape
    sx, xx = sx_grid(fit, H, W)
    body = base["mask"]
    rep = {"enclosed_holes_filled": nenc}
    mode = cfg["mode"]
    root_ext = None
    if mode == "seam":
        m = (alpha > 0.5) & (xx >= sx + base["seam_cfg"]["offset"] - base["seam_cfg"].get("head_overlap", 0))
        # contract checks against the base body
        lo, hi = base["contract"]["seam_columns"]; tol = base["contract"]["seam_tolerance_px"]
        nm = ndi.binary_fill_holes(alpha > 0.5); bad = 0
        for x in range(lo, hi):
            cb = np.where(body[:, x])[0]; cn = np.where(nm[:, x])[0]
            if len(cb) == 0 or len(cn) == 0 or abs(cb.min() - cn.min()) > tol or abs(cb.max() - cn.max()) > tol:
                bad += 1
        extra = int((nm & ~body & (xx < sx)).sum())
        rep.update({"seam_bad_columns": bad, "extra_px_behind_seam": extra})
        piv = None
    else:
        diff = np.abs(raw - base["raw"]).sum(2)
        outside = (alpha > 0.5) & ~body & (diff > 60)
        if mode == "loop":
            navy = (raw[..., 0] < 110) & (raw[..., 1] < 110) & (raw[..., 2] < 170)
            coral = (raw[..., 0] > 200) & (raw[..., 1] > 90) & (raw[..., 1] < 170) & (raw[..., 2] < 150)
            inside = body & (diff > 110) & (navy | coral)
            m = ndi.binary_closing(inside, iterations=3)
            m = ndi.binary_fill_holes(m); m = ndi.binary_opening(m, iterations=3)
        else:
            inside = body & (diff > cfg.get("inside_thr", 110))
            m = outside | inside
            if cfg.get("closing"): m = ndi.binary_closing(m, iterations=cfg["closing"])
            m = ndi.binary_opening(m, iterations=2); m = ndi.binary_fill_holes(m)
        lab, n = ndi.label(m)
        if n > 1:
            sizes = ndi.sum(m, lab, range(1, n + 1)); m = lab == (1 + int(np.argmax(sizes)))
        rep["area_px"] = int(m.sum())
        root_ext = cfg.get("root_extrude")
    # alpha: soft outside the body, solid inside
    a = np.where(m & ~body, alpha, 0.0) + np.where(m & body, 1.0, 0.0)
    a = np.clip(a, 0, 1).astype(np.float32)
    if mode == "seam":
        a = np.where(m, alpha, 0.0).astype(np.float32)
    # hidden root so behind-parts can swing without opening a gap
    ch = np.concatenate([locked, cov, shade[..., None]], axis=2)
    if root_ext:
        navy_px = (locked[..., 0] < 110) & (locked[..., 1] < 110) & (locked[..., 2] < 170)
        src = ndi.binary_erosion(m & ~body, iterations=6) & ~ndi.binary_dilation(navy_px, iterations=3) & ndi.binary_dilation(body, iterations=70)
        d, idx = ndi.distance_transform_edt(~src, return_indices=True)
        ext = body & (d < root_ext) & ~m
        ch[ext] = ch[idx[0][ext], idx[1][ext]]
        a = np.where(ext, 1.0, a).astype(np.float32)
    # pivot (canvas px)
    ys, xs = np.where(m)
    if mode == "seam":
        pivot = [float(sx[ys.min():ys.max()].mean() + base["seam_cfg"]["offset"]), float((ys.min() + ys.max()) / 2)]
    elif cfg["layer"] == "behind":
        contact = m & ndi.binary_dilation(body, iterations=6); cy, cx = ndi.center_of_mass(contact); pivot = [float(cx), float(cy)]
    elif cfg["slot"] == "sidefin":
        k = max(5, int(len(xs) * 0.03)); sel = np.argsort(xs)[-k:]; pivot = [float(xs[sel].mean()), float(ys[sel].mean())]
    else:
        cy, cx = ndi.center_of_mass(m & body) if (m & body).any() else ndi.center_of_mass(m); pivot = [float(cx), float(cy)]
    rep["bbox"] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    return {"ch": ch, "alpha": a, "pivot": pivot, "report": rep}

def make_torso(base, fit, pal, cfg):
    locked, cov, shade = unmix(base["rgb"], base["alpha"], pal)
    H, W = base["alpha"].shape
    sx, xx = sx_grid(fit, H, W)
    cut = sx + cfg["seam"]["offset"]
    torso_m = base["mask"] & (xx < cut)
    ch = np.concatenate([locked, cov, shade[..., None]], axis=2)
    a = np.where(torso_m, base["alpha"], 0.0).astype(np.float32)
    ext = cfg["seam"]["torso_extend"]
    for r in range(H):                         # extend the torso forward under the head
        cols = np.where(torso_m[r])[0]
        if len(cols) == 0: continue
        last = cols.max()
        for dx in range(1, ext + 1):
            xn = last + dx
            if xn < W and base["mask"][r, xn]:
                ch[r, xn] = ch[r, last]; a[r, xn] = 1.0
    ys, xs = np.where(a > 0.5)
    return {"ch": ch, "alpha": a, "pivot": [float(xs.mean()), float(ys.mean())], "report": {"bbox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]}}

def downscale(img, s, premult_alpha=None):
    h, w = img.shape[:2]; size = (max(1, round(w * s)), max(1, round(h * s)))
    return np.asarray(Image.fromarray(img).resize(size, Image.LANCZOS))

def pack(frames, pad=2, width=1024):
    order = sorted(frames, key=lambda k: -frames[k]["h"])
    x = y = rowh = pad; out = {}
    for k in order:
        w, h = frames[k]["w"], frames[k]["h"]
        if x + w + pad > width:
            x = pad; y += rowh + pad; rowh = 0
        out[k] = (x, y); x += w + pad; rowh = max(rowh, h)
    return out, y + rowh + pad

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); args = ap.parse_args()
    man = json.load(open(ROOT / "art" / "parts.json")); pal = load_palette()
    S = man["atlas_scale"]; problems = []; warnings = []; report = {}
    rig = {"version": 2, "atlas": {"image": "atlas.png", "tint": "atlas_tint.png", "scale": S, "display_scale": man["display_scale"]},
           "palette": "art/palette.json", "frames": {}, "classes": {}}
    sheet_items = []; layers = {}
    for cname, cfg in man["classes"].items():
        base, fit = make_base(cfg); body = base["mask"]; alpha = base["alpha"]; H, W = alpha.shape
        cls = {"draw_order": cfg["draw_order"], "slots": {}, "parts": {}}
        entries = {"torso": make_torso(base, fit, pal, cfg)}
        ys, xs = np.where(body); rig["origin"] = [round(float((xs.min() + xs.max()) / 2 * S), 1), round(float((ys.min() + ys.max()) / 2 * S), 1)]
        for pname, pc in cfg["parts"].items():
            print("  extracting", pname, flush=True)
            entries[pname] = extract_part(pname, pc, base, fit, pal)
            r = entries[pname]["report"]
            if pc["mode"] == "seam":
                if r["seam_bad_columns"] > cfg["contract"]["max_bad_columns"]:
                    problems.append(f"{pname}: silhouette differs from the base at {r['seam_bad_columns']} seam columns")
                if r["extra_px_behind_seam"] > cfg["contract"]["warn_extra_px_behind_seam"]:
                    warnings.append(f"{pname}: {r['extra_px_behind_seam']} px drawn behind the seam (unrequested additions; ignored, but the generator is drifting)")
            elif r["area_px"] < 2000:
                problems.append(f"{pname}: extracted area is only {r['area_px']} px (extraction probably failed)")
        report[cname] = {k: v["report"] for k, v in entries.items()}
        # frames: keep FULL-canvas arrays so every part is later scaled on the same pixel grid.
        # Colours are bled outwards into the transparent area first, so filtering never mixes in black/white fringes.
        for pname, e in entries.items():
            pc = cfg["parts"].get(pname, {"slot": "torso", "layer": "middle"})
            al = e["alpha"]; ch = e["ch"].copy()
            opaque = al > 0.5
            _, idx = ndi.distance_transform_edt(~opaque, return_indices=True)
            ch[~opaque] = ch[idx[0][~opaque], idx[1][~opaque]]
            rgba = np.dstack([np.clip(ch[..., 0:3], 0, 255), al * 255]).astype(np.float32)
            tint = np.dstack([np.clip(ch[..., 3:6], 0, 1) * 255, np.clip(ch[..., 6], 0, 1) * 255]).astype(np.float32)
            layers[pname] = (rgba, tint, e["report"]["bbox"], e["pivot"], pc)
        cls["parts"] = {}
    for w in warnings: print("WARNING:", w)
    if args.check or problems:
        for p in problems: print("CONTRACT FAILURE:", p)
        if not problems: print("contract OK for all parts")
        Path(ROOT / "build").mkdir(exist_ok=True); json.dump(report, open(ROOT / "build" / "report.json", "w"), indent=1)
        if args.check or problems: sys.exit(1 if problems else 0)
    # ---- downscale on the shared grid, trim, pack
    frames = {}
    def ds(arr, size):
        return np.dstack([np.asarray(Image.fromarray(np.ascontiguousarray(arr[..., c]), "F").resize(size, Image.LANCZOS)) for c in range(arr.shape[2])])
    for pname, (rgba, tint, bb, piv, pc) in layers.items():
        size = (round(rgba.shape[1] * S), round(rgba.shape[0] * S))
        rs = ds(rgba, size); ts = ds(tint, size)
        al = np.clip(rs[..., 3] / 255.0, 0, 1)
        ys, xs = np.where(al > 0.01); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        img = np.dstack([np.clip(rs[y0:y1, x0:x1, :3], 0, 255), al[y0:y1, x0:x1] * 255]).astype(np.uint8)
        timg = np.clip(ts[y0:y1, x0:x1], 0, 255).astype(np.uint8)
        frames[pname] = {"img": img, "timg": timg, "w": img.shape[1], "h": img.shape[0], "off": (int(x0), int(y0)), "pivot": piv, "pc": pc}
    pos, hh = pack(frames)
    atlas = np.zeros((hh, 1024, 4), np.uint8); tatlas = np.zeros((hh, 1024, 4), np.uint8)
    for k, (x, y) in pos.items():
        f = frames[k]; atlas[y:y + f["h"], x:x + f["w"]] = f["img"]; tatlas[y:y + f["h"], x:x + f["w"]] = f["timg"]
        rig["frames"][k] = {"x": x, "y": y, "w": f["w"], "h": f["h"], "ox": f["off"][0], "oy": f["off"][1],
                            "pivot": [round(f["pivot"][0] * S, 2), round(f["pivot"][1] * S, 2)]}
    cfg = man["classes"]["fish"]
    c = {"draw_order": cfg["draw_order"], "layers": {}, "slots": {"torso": ["torso"]}, "parts": {}}
    for pname, pc in cfg["parts"].items():
        c["slots"].setdefault(pc["slot"], []).append(pname)
        c["parts"][pname] = {"frame": pname, "slot": pc["slot"], "layer": pc["layer"], "anchors": pc.get("anchors", {}),
                             "skin_group": pc.get("skin_group", "default")}
        if "needs_review" in pc: c["parts"][pname]["needs_review"] = pc["needs_review"]
    c["parts"]["torso"] = {"frame": "torso", "slot": "torso", "layer": "middle", "anchors": {}, "skin_group": "body"}
    rig["classes"]["fish"] = c
    out = ROOT / "assets" / "fish"; out.mkdir(parents=True, exist_ok=True)
    Image.fromarray(atlas, "RGBA").save(out / "atlas.png", optimize=True); Image.fromarray(tatlas, "RGBA").save(out / "atlas_tint.png", optimize=True)
    json.dump(rig, open(out / "rig.json", "w"), indent=1)
    Path(ROOT / "build").mkdir(exist_ok=True); json.dump(report, open(ROOT / "build" / "report.json", "w"), indent=1)
    print(f"atlas {atlas.shape[1]}x{atlas.shape[0]}, {len(frames)} frames -> assets/fish/")

if __name__ == "__main__":
    main()
