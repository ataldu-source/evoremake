"""Reassemble the rig from art/rig and write art/rig/rig_preview.png (builds + swim poses)."""
from PIL import Image, ImageDraw
import json
from pathlib import Path
O=str(Path(__file__).resolve().parent.parent/"art"/"rig")+"/"
R=json.load(open(O+"rig.json")); P=R["parts"]
L={k:Image.open(O+P[k]["file"]) for k in ["tail","dorsal","body","sidefin","horn"]}
def rot(img,ang,piv): return img.rotate(ang,center=tuple(piv),resample=Image.BICUBIC)
def build(parts,tail=0,dorsal=0,fin=0,horn=0,bg=(30,90,140)):
    c=Image.new("RGBA",(1024,1024),bg+(255,))
    for k in R["order"]:
        if k!="body" and k not in parts: continue
        im=L[k]
        if k=="tail": im=rot(im,tail,P[k]["pivot"])
        if k=="dorsal": im=rot(im,dorsal,P[k]["pivot"])
        if k=="sidefin": im=rot(im,fin,P[k]["pivot"])
        if k=="horn": im=rot(im,horn,P[k]["pivot"])
        c.alpha_composite(im)
    return c.crop((60,150,1010,760))
cell=(475,305)
def sm(im): return im.resize(cell,Image.LANCZOS)
rows=[
 [build(["tail","dorsal","sidefin","horn"]), build(["tail"]), build(["dorsal","sidefin"]), build(["horn","sidefin"])],
 [build(["tail","dorsal","sidefin","horn"],tail=-14,fin=8), build(["tail","dorsal","sidefin","horn"],tail=0,fin=-8,dorsal=3), build(["tail","dorsal","sidefin","horn"],tail=14,fin=8,dorsal=-3), build(["tail","dorsal","sidefin","horn"],tail=0,horn=-6,fin=-8)],
]
sheet=Image.new("RGB",(cell[0]*4,cell[1]*2))
for r,row in enumerate(rows):
    for c,im in enumerate(row): sheet.paste(sm(im).convert("RGB"),(c*cell[0],r*cell[1]))
sheet.save(O+"rig_preview.png"); print(sheet.size)
