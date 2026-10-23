"""Compare how the assembled fish reads at different internal resolutions. Writes docs/res_test.png."""
from pathlib import Path
from PIL import Image, ImageDraw
import json
ROOT=Path(__file__).resolve().parent.parent
O=ROOT/"art"/"rig"
R=json.load(open(O/"rig.json")); P=R["parts"]
c=Image.new("RGBA",(1024,1024),(0,0,0,0))
for k in R["order"]: c.alpha_composite(Image.open(O/P[k]["file"]))
fish=c.crop(c.getbbox())
def scene(w,h,fishlen,method):
    f=fish.resize((fishlen,int(fish.height*fishlen/fish.width)),method)
    bg=Image.new("RGBA",(w,h),(35,105,150,255)); ImageDraw.Draw(bg).rectangle((0,int(h*.8),w,h),fill=(214,196,140,255))
    bg.alpha_composite(f,(int(w*.35),int(h*.35))); return bg
def up(im,box,s): return im.crop(box).resize(((box[2]-box[0])*s,(box[3]-box[1])*s),Image.NEAREST)
panels=[("A  480x270, nearest from big art (naive)",up(scene(480,270,72,Image.NEAREST),(150,80,270,170),4)),
        ("B  480x270, pre-downscaled (Lanczos)",up(scene(480,270,72,Image.LANCZOS),(150,80,270,170),4)),
        ("C  960x540, pre-downscaled (Lanczos)",up(scene(960,540,144,Image.LANCZOS),(300,160,540,340),2))]
W=sum(p[1].width for p in panels)+80; H=max(p[1].height for p in panels)+60
sheet=Image.new("RGB",(W,H),(245,245,245)); d=ImageDraw.Draw(sheet); x=20
for t,im in panels: sheet.paste(im.convert("RGB"),(x,40)); d.text((x,12),t,fill=(0,0,0)); x+=im.width+20
sheet.save(ROOT/"docs"/"res_test.png"); print("wrote docs/res_test.png")
