"""Extract rig parts from in-place Gemini edits of the base body.

Run from anywhere:  python tools/extract_parts.py
Inputs : art/raw/body_base.jpg + art/raw/edit_<part>.jpg (same canvas, same body position)
Outputs: art/rig/parts/*.png (full 1024x1024 RGBA layers) + art/rig/rig.json (order, bbox, pivots)
See docs/ART_STYLE.md for how the edits are generated.
"""
from PIL import Image
import numpy as np, json
from scipy import ndimage as ndi
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
U=str(ROOT/"art"/"raw")+"/"; O=str(ROOT/"art"/"rig")+"/"
(ROOT/"art"/"rig"/"parts").mkdir(parents=True,exist_ok=True)
def key(path):
    a=np.asarray(Image.open(path).convert("RGB")).astype(float)
    border=np.concatenate([a[:20].reshape(-1,3),a[-20:].reshape(-1,3),a[:,:20].reshape(-1,3),a[:,-20:].reshape(-1,3)])
    bg=np.median(border,axis=0)
    mag=lambda x: np.minimum(x[...,0],x[...,2])-x[...,1]
    t=np.clip(mag(a)/mag(bg),0,1); t=np.where(t<0.12,0,t); t=np.where(t>0.85,1,t)
    alpha=1-t; af=np.clip(alpha,1e-3,1)[...,None]
    fg=np.clip((a-t[...,None]*bg)/af,0,255)
    return a,fg,alpha
oa,ofg,oal=key(U+"body_base.jpg")
body=oal>0.5
body=ndi.binary_fill_holes(body)
bodyd=ndi.binary_dilation(body,iterations=3)
def rgba(fg,alpha): return Image.fromarray(np.dstack([fg,np.clip(alpha,0,1)*255]).astype(np.uint8),"RGBA")
rgba(ofg,np.where(body,oal,0)*1.0).save(O+"parts/body.png")
files={"tail":"edit_tail.jpg","dorsal":"edit_dorsal.jpg","horn":"edit_horn.jpg","sidefin":"edit_sidefin.jpg"}
behind={"tail","dorsal"}
meta={}
for name,f in files.items():
    a,fg,al=key(U+f)
    outside=(al>0.5)&~body&(np.abs(a-oa).sum(axis=2)>60)
    diff=np.abs(a-oa).sum(axis=2)
    inside=body&(diff>(45 if name=='horn' else 110))
    if name=="sidefin":
        # keep only navy outline + coral fill, then fill the closed loop (drops the soft drop-shadow)
        navy=(a[...,0]<110)&(a[...,1]<110)&(a[...,2]<170)
        coral=(a[...,0]>200)&(a[...,1]>90)&(a[...,1]<170)&(a[...,2]<150)
        cand=inside&(navy|coral)
        cand=ndi.binary_closing(cand,iterations=3)
        m=ndi.binary_fill_holes(cand)
        m=ndi.binary_opening(m,iterations=3)
    else:
        m=outside|inside
        if name=='horn': m=ndi.binary_closing(m,iterations=5)
        m=ndi.binary_opening(m,iterations=2)
        m=ndi.binary_fill_holes(m)
    lab,n=ndi.label(m)
    if n>1:
        sizes=ndi.sum(m,lab,range(1,n+1)); m=lab==(1+int(np.argmax(sizes)))
    # alpha: soft where outside body, hard inside
    alpha=np.where(m&~body, al, 0.0)+np.where(m&body,1.0,0.0)
    alpha=np.clip(alpha,0,1)
    layer_fg=fg.copy()
    if name in behind:
        # extrude part colors under the body so rotating the part never opens a gap
        navy_px=(fg[...,0]<110)&(fg[...,1]<110)&(fg[...,2]<170)
        src=ndi.binary_erosion(m&~body,iterations=6)&~ndi.binary_dilation(navy_px,iterations=3)&ndi.binary_dilation(body,iterations=70)
        d,idx=ndi.distance_transform_edt(~src,return_indices=True)
        ext=body&(d<34)&~m
        layer_fg[ext]=fg[idx[0][ext],idx[1][ext]]
        alpha=np.where(ext,1.0,alpha)
    img=rgba(layer_fg,alpha)
    # pivot
    ys,xs=np.where(m)
    if name in behind:
        contact=m&ndi.binary_dilation(body,iterations=6)
        cy,cx=ndi.center_of_mass(contact)
    elif name=="sidefin":
        k=max(5,int(len(xs)*0.03)); sel=np.argsort(xs)[-k:]; cx,cy=xs[sel].mean(),ys[sel].mean()
    else:
        cy,cx=ndi.center_of_mass(m&body) if (m&body).any() else ndi.center_of_mass(m)
    bb=(int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1)
    img.save(O+f"parts/{name}.png")   # full-canvas 1024x1024 layer in body coordinates
    meta[name]={"file":f"parts/{name}.png","layer":"behind" if name in behind else "front","bbox":bb,"pivot":[round(float(cx),1),round(float(cy),1)],"area_px":int(m.sum())}
    print(name,meta[name])
ys,xs=np.where(body); meta["body"]={"file":"parts/body.png","bbox":[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]}
json.dump({"canvas":[1024,1024],"order":["tail","dorsal","body","sidefin","horn"],"parts":meta},open(O+"rig.json","w"),indent=1)
