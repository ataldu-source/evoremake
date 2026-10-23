"""Prototype: split the base body into TORSO + HEAD at a seam just in front of the gill line,
then tint torso+head together and the fins separately, to prove (a) the seam is invisible when the tints match and
(b) body skins can be runtime tints instead of extra art. Writes docs/head_tint_test.png (and build/headtest/*).
Run from anywhere:  python tools/head_tint_test.py
"""
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parent.parent
os.chdir(ROOT)
T=str(ROOT/"build"/"headtest")+"/"; os.makedirs(T,exist_ok=True)
from PIL import Image, ImageDraw
import numpy as np, json, colorsys
from scipy import ndimage as ndi
O="art/rig/"; R=json.load(open(O+"rig.json")); P=R["parts"]
L={k:Image.open(O+P[k]["file"]).convert("RGBA") for k in R["order"]}
body=np.asarray(L["body"]).astype(float); H,W,_=body.shape
mask=body[...,3]>127
# --- find the gill stroke (navy pixels well inside the body, left of the eye) and fit the seam x=f(y)
inner=ndi.binary_erosion(mask,iterations=30)
navy=(body[...,0]<110)&(body[...,1]<110)&(body[...,2]<170)
ys,xs=np.where(inner&navy)
sel=(xs>=560)&(xs<=660)&(ys>=410)&(ys<=605)
y,x=ys[sel],xs[sel]; print("gill pixels",len(x), "x range",x.min(),x.max(),"y range",y.min(),y.max())
co=np.polyfit(y,x,2); f=np.poly1d(co)
y0,y1=y.min(),y.max(); s0=np.polyder(f)(y0); s1=np.polyder(f)(y1)
def seam_x(yy):
    yy=np.asarray(yy,float); out=f(np.clip(yy,y0,y1))
    out=np.where(yy<y0,f(y0)+s0*(yy-y0),out); out=np.where(yy>y1,f(y1)+s1*(yy-y1),out); return out
yy=np.arange(H)[:,None]; xx=np.arange(W)[None,:]
sx=seam_x(np.arange(H))[:,None]
head_m=mask&(xx>=sx+14)          # seam just IN FRONT of the gill stroke: stroke + crescent shading stay on the torso
torso_m=mask&~head_m
# torso extension forward (hidden under the head)
ext=np.zeros_like(mask); torso=body.copy(); torso[~torso_m]=0
for r in range(H):
    cols=np.where(torso_m[r])[0]
    if len(cols)==0: continue
    last=cols.max(); c=body[r,last].copy()
    for dx in range(1,46):
        xnew=last+dx
        if xnew<W and mask[r,xnew]: torso[r,xnew]=c
head=body.copy(); head[~head_m]=0
Image.fromarray(torso.astype(np.uint8),"RGBA").save(T+"torso.png")
Image.fromarray(head.astype(np.uint8),"RGBA").save(T+"head.png")
json.dump({"seam_poly":[float(c) for c in co],"y_range":[int(y0),int(y1)]},open(T+"seam.json","w"))
print("seam coeffs",co)

# ---------------- tint variants ----------------
from PIL import Image, ImageDraw
import numpy as np, json
O="art/rig/"; R=json.load(open(O+"rig.json")); P=R["parts"]
L={k:Image.open(O+P[k]["file"]).convert("RGBA") for k in R["order"]}
torso=Image.open(T+"torso.png"); head=Image.open(T+"head.png")
def smooth(x,a,b): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
def recolor(img,teal=0,yellow=0,coral=0,sat=1.0):
    """Hue-shift tint: teal family, yellow family and coral family can move independently (degrees)."""
    a=np.asarray(img.convert("RGBA")).astype(np.uint8)
    hsv=np.asarray(Image.fromarray(a[...,:3],"RGB").convert("HSV")).astype(float)
    h=hsv[...,0]*360/255; s=hsv[...,1]/255; v=hsv[...,2]/255
    colorful=smooth(s,0.18,0.40)*smooth(v,0.38,0.60)     # skip the navy outline and greys
    wt=smooth(h,140,165)*(1-smooth(h,200,215))*colorful   # teal band
    wy=smooth(h,30,42)*(1-smooth(h,62,78))*colorful      # yellow band
    wc=(1-smooth(h,8,22))*colorful*(h<40)+smooth(h,335,350)*colorful*(h>300)   # coral/red band
    hn=(h+wt*teal+wy*yellow+wc*coral)%360
    sn=np.clip(s*(1+(sat-1)*np.maximum(wt,wy)),0,1)
    out=np.dstack([hn*255/360,sn*255,v*255]).astype(np.uint8)
    rgb=np.asarray(Image.fromarray(out,"HSV").convert("RGB"))
    return Image.fromarray(np.dstack([rgb,a[...,3]]),"RGBA")
def rot(img,ang,piv): return img.rotate(ang,center=tuple(piv),resample=Image.BICUBIC)
def build(teal,yellow,fin_coral,horn=True,bg=(30,90,140),head_extra_shift=0,seam=False):
    c=Image.new("RGBA",(1024,1024),bg+(255,))
    c.alpha_composite(recolor(L["tail"],coral=fin_coral))
    c.alpha_composite(recolor(L["dorsal"],coral=fin_coral))
    c.alpha_composite(recolor(torso,teal,yellow))
    c.alpha_composite(recolor(head,teal+head_extra_shift,yellow))
    c.alpha_composite(recolor(L["sidefin"],coral=fin_coral))
    if horn: c.alpha_composite(recolor(L["horn"],teal=teal,coral=fin_coral))
    return c.crop((60,150,1010,760)).resize((475,305),Image.LANCZOS)
# (teal shift, yellow shift, fin coral shift)
V=[("original",0,0,0),("violet body, cream belly",95,5,-20),("reef orange body",-150,10,-30),("lime body, blue fins",-70,0,210),("pink body, teal fins",150,-25,150),
   ("MISMATCH test: head 25deg off",0,0,0)]
tiles=[]
for name,t,y,c in V:
    extra=25 if name.startswith("MISMATCH") else 0
    tiles.append((name,build(t,y,c,head_extra_shift=extra)))
sheet=Image.new("RGB",(475*3,(305+22)*2),(240,240,240)); d=ImageDraw.Draw(sheet)
for i,(n,im) in enumerate(tiles):
    x=(i%3)*475; yv=(i//3)*(305+22)
    sheet.paste(im.convert("RGB"),(x,yv+22)); d.text((x+8,yv+6),n,fill=(0,0,0))
sheet.save(str(ROOT/"docs"/"head_tint_test.png")); print(sheet.size)
# seam visualisation: original fish with the cut line + head/torso tinted differently
c=Image.new("RGBA",(1024,1024),(30,90,140,255))
for k in ["tail","dorsal"]: c.alpha_composite(L[k])
c.alpha_composite(torso); 
h2=head.copy(); a=np.asarray(h2).copy(); a[...,0]=np.clip(a[...,0]*0.6+110,0,255); h2=Image.fromarray(a,"RGBA"); c.alpha_composite(h2)
c.crop((380,250,800,760)).save(T+"seam_view.png")
