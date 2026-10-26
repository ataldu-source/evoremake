"""Shared image helpers for the art pipeline (keying, palette, tint masks, seam)."""
from pathlib import Path
import json, colorsys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
MAGENTA_EDGE = 20            # border width used to estimate the background colour

def mag(x):                  # "magenta-ness" of an RGB array
    return np.minimum(x[..., 0], x[..., 2]) - x[..., 1]

def load_rgb(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float32)

def key_connected(path):
    """Key out the #FF00FF background.
    Only magenta connected to the canvas border is transparent; enclosed magenta (inside an open mouth) becomes solid
    dark navy together with its fringe. Returns (raw, rgb, alpha, enclosed_count)."""
    a = load_rgb(path)
    b = MAGENTA_EDGE
    border = np.concatenate([a[:b].reshape(-1, 3), a[-b:].reshape(-1, 3), a[:, :b].reshape(-1, 3), a[:, -b:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    t = np.clip(mag(a) / mag(bg), 0, 1)
    isbg = t > 0.5
    lab, n = ndi.label(isbg)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    outer = np.isin(lab, list(edge))
    enclosed = isbg & ~outer
    near_out = ndi.binary_dilation(outer, iterations=3)
    t2 = np.where(outer | ((t > 0.12) & near_out), t, 0)
    t2 = np.where(t2 < 0.12, 0, t2)
    t2 = np.where(t2 > 0.85, 1, t2)
    alpha = 1 - t2
    af = np.clip(alpha, 1e-3, 1)[..., None]
    rgb = np.clip((a - t2[..., None] * bg) / af, 0, 255)
    fringe = ndi.binary_dilation(enclosed, iterations=3) & (t > 0.10) & ~near_out
    fill = enclosed | fringe
    rgb[fill] = (24, 26, 64)
    alpha = np.where(fill, 1.0, alpha).astype(np.float32)
    return a, rgb.astype(np.float32), alpha, int(enclosed.sum())

# ----------------------------------------------------------------------------------------------------------------
# palette + tint masks
FAMILIES = ["teal", "yellow", "coral"]

def load_palette(path=None):
    path = path or ROOT / "art" / "palette.json"
    return json.load(open(path))

def ramp_points(pal, family):
    """Default ramp stops of a family: list of (shade, rgb) sorted by shade."""
    pts = sorted((e["shade"], np.array(e["rgb"], np.float32)) for e in pal["entries"] if e["family"] == family)
    if pts[0][0] > 0:
        pts.insert(0, (0.0, pts[0][1]))
    if pts[-1][0] < 1:
        pts.append((1.0, pts[-1][1]))
    return pts

def ramp_eval(points, s):
    """Piecewise-linear colour for shade s (0..1). points: [(shade, rgb)...]."""
    s = np.asarray(s, np.float32)
    xs = np.array([p[0] for p in points], np.float32)
    cols = np.stack([p[1] for p in points])
    out = np.stack([np.interp(s, xs, cols[:, c]) for c in range(3)], axis=-1)
    return out.astype(np.float32)

def unmix(rgb, alpha, pal, tol=11.0, chunk=15000):
    """Palette-lock + tint-mask extraction.
    Every opaque pixel is modelled as  p = mix(O, ramp_f(s), cov)  with O a non-tint palette colour (navy, white, cream...)
    and f a tintable family. Returns locked_rgb, cov (H,W,3 teal/yellow/coral), shade (H,W)."""
    H, W, _ = rgb.shape
    locked = rgb.copy()
    cov = np.zeros((H, W, 3), np.float32)
    shade = np.zeros((H, W), np.float32)
    others = np.array([e["rgb"] for e in pal["entries"] if e["family"] == "none"], np.float32)      # (m,3)
    ramps = []
    for f in FAMILIES:
        pts = ramp_points(pal, f)
        ss = np.linspace(0, 1, 21, dtype=np.float32)
        ramps.append((ss, ramp_eval(pts, ss)))
    idx = np.argwhere(alpha > 0.02)
    P = rgb[idx[:, 0], idx[:, 1]]
    n = len(P)
    best_res = np.full(n, 1e9, np.float32); best_f = np.full(n, -1); best_s = np.zeros(n, np.float32)
    best_a = np.zeros(n, np.float32); best_o = np.zeros(n, int)
    for lo in range(0, n, chunk):
        p = P[lo:lo + chunk]
        for fi, (ss, R) in enumerate(ramps):
            # candidate pure colours, shape (K,3) ; mixes with each other colour O
            D = others[None, :, :] - R[:, None, :]                       # (K,m,3)
            num = ((p[:, None, None, :] - R[None, :, None, :]) * D[None]).sum(-1)     # (n,K,m)
            den = (D ** 2).sum(-1)[None] + 1e-6
            a = np.clip(num / den, 0, 1)                                 # fraction of O
            rec = R[None, :, None, :] + a[..., None] * D[None]
            res = np.linalg.norm(p[:, None, None, :] - rec, axis=-1)     # (n,K,m)
            flat = res.reshape(len(p), -1)
            j = flat.argmin(1)
            r = flat[np.arange(len(p)), j]
            k, o = np.divmod(j, others.shape[0])
            better = r < best_res[lo:lo + len(p)]
            sl = slice(lo, lo + len(p))
            best_res[sl] = np.where(better, r, best_res[sl]); best_f[sl] = np.where(better, fi, best_f[sl])
            best_s[sl] = np.where(better, ss[k], best_s[sl])
            best_a[sl] = np.where(better, a[np.arange(len(p)), k, o], best_a[sl]); best_o[sl] = np.where(better, o, best_o[sl])
    ok = best_res < tol
    c = 1 - best_a
    tinted = ok & (c > 0.04)
    ys, xs = idx[:, 0], idx[:, 1]
    # tint-covered pixels: rebuilt from the model (this is the palette lock)
    for fi, (ss, R) in enumerate(ramps):
        sel = tinted & (best_f == fi)
        if not sel.any():
            continue
        col = ramp_eval(ramp_points(pal, FAMILIES[fi]), best_s[sel])
        o = others[best_o[sel]]
        a = best_a[sel][:, None]
        locked[ys[sel], xs[sel]] = col * (1 - a) + o * a
        cov[ys[sel], xs[sel], fi] = c[sel]
        shade[ys[sel], xs[sel]] = best_s[sel]
    # non-tint pixels that sit on a palette colour: lock them too
    d = np.linalg.norm(P[:, None, :] - others[None], axis=-1)
    jn = d.argmin(1); near = (d.min(1) < tol) & ~tinted
    locked[ys[near], xs[near]] = others[jn[near]]
    # second pass: antialiased boundaries between two palette colours (e.g. teal|yellow belly line)
    rest = np.where(~ok & ~near)[0]
    if len(rest):
        ents = pal["entries"]; E = np.array([e["rgb"] for e in ents], np.float32)
        fam = [FAMILIES.index(e["family"]) if e["family"] in FAMILIES else -1 for e in ents]
        sh = np.array([e["shade"] for e in ents], np.float32)
        I, J = np.triu_indices(len(E), 1)
        A, D = E[I], E[J] - E[I]; den = (D ** 2).sum(1) + 1e-6
        for lo in range(0, len(rest), chunk):
            r = rest[lo:lo + chunk]; p = P[r]
            a2 = np.clip(((p[:, None, :] - A[None]) * D[None]).sum(-1) / den[None], 0, 1)
            rec = A[None] + a2[..., None] * D[None]
            res = np.linalg.norm(p[:, None, :] - rec, axis=-1)
            k = res.argmin(1); rr = res[np.arange(len(r)), k]; aa = a2[np.arange(len(r)), k]
            good = rr < tol * 1.3
            for t_, (g, kk, a_) in enumerate(zip(good, k, aa)):
                if not g:
                    continue
                y, x = ys[r[t_]], xs[r[t_]]
                i, j = I[kk], J[kk]
                locked[y, x] = rec[t_, kk]
                wsum = 0.0; ssum = 0.0
                for ent, w in ((i, 1 - a_), (j, a_)):
                    if fam[ent] >= 0 and w > 0.02:
                        cov[y, x, fam[ent]] += w; wsum += w; ssum += w * sh[ent]
                if wsum > 0:
                    shade[y, x] = ssum / wsum
    return locked, cov, shade

# ----------------------------------------------------------------------------------------------------------------
# seam between torso and head (class-specific; derived from the base body's gill stroke)
def fit_seam(base_rgb, base_alpha, cfg):
    mask = base_alpha > 0.5
    inner = ndi.binary_erosion(mask, iterations=30)
    navy = (base_rgb[..., 0] < 110) & (base_rgb[..., 1] < 110) & (base_rgb[..., 2] < 170)
    ys, xs = np.where(inner & navy)
    x0, x1 = cfg["gill_x"]; y0, y1 = cfg["gill_y"]
    sel = (xs >= x0) & (xs <= x1) & (ys >= y0) & (ys <= y1)
    y, x = ys[sel], xs[sel]
    co = np.polyfit(y, x, 2)
    return np.poly1d(co), int(y.min()), int(y.max())

def seam_x(fit, yy):
    """Near-vertical seam: the fitted curve inside the gill stroke, straight up/down beyond it (S3i)."""
    f, y0, y1 = fit
    return f(np.clip(np.asarray(yy, np.float32), y0, y1))

# ----------------------------------------------------------------------------------------------------------------
# skins (reference implementation of the recolour shader)
def load_skins(path=None):
    path = path or ROOT / "art" / "skins.json"
    return json.load(open(path))["skins"]

def skin_ramp(pal, skin, family):
    """Ramp points for a family under a skin; missing family -> default ramp. Skin gives stops evenly spread over 0..1
    (3 stops: 0, .5, 1; 2 stops: 0, .5 with the last colour held to 1)."""
    if family not in skin:
        return ramp_points(pal, family)
    cols = [np.array(c, np.float32) for c in skin[family]]
    shades = [0.0, 0.5, 1.0][:len(cols)]
    pts = list(zip(shades, cols))
    if pts[-1][0] < 1:
        pts.append((1.0, pts[-1][1]))
    return pts

def apply_skin(base_rgb, cov, shade, pal, skin_name, skins, only=None):
    """out = base + sum_f cov_f * (skin_ramp_f(shade) - default_ramp_f(shade))  (linear, so it survives downscaling)."""
    skin = skins[skin_name]
    out = base_rgb.astype(np.float32).copy()
    for fi, f in enumerate(FAMILIES):
        if only is not None and f not in only:
            continue
        d = ramp_eval(skin_ramp(pal, skin, f), shade) - ramp_eval(ramp_points(pal, f), shade)
        out += cov[..., fi:fi + 1] * d
    return np.clip(out, 0, 255)
