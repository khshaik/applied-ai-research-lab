#!/usr/bin/env python3
"""Render the sketch-style VDCM end-to-end workflow as PNG and SVG.

The figure is a conceptual communication artifact. It uses repository-owned
geometry and text, performs no network access, and does not encode an empirical
result. Every workflow transition has an explicit directional arrowhead.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
W, H = 2800, 1800

PAPER = "#FFFDF8"
WHITE = "#FFFFFF"
NAVY = "#0B2554"
ORANGE = "#B84408"
INK = "#111111"
MUTED = "#4D4D4D"
SOFT_BLUE = "#F3F7FF"
SOFT_ORANGE = "#FFF7F0"
SOFT_GREY = "#F8F6F1"

HAND_BOLD = Path("/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf")
COMIC = Path("/System/Library/Fonts/Supplemental/Comic Sans MS.ttf")
COMIC_BOLD = Path("/System/Library/Fonts/Supplemental/Comic Sans MS Bold.ttf")
FALLBACK = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FALLBACK_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def font(size: int, *, heading: bool = False, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if heading:
        candidates.extend([HAND_BOLD, COMIC_BOLD])
    elif bold:
        candidates.extend([COMIC_BOLD, HAND_BOLD, FALLBACK_BOLD])
    else:
        candidates.extend([COMIC, FALLBACK])
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


STEPS = [
    (1, "DEFINE DELIVERY\nOUTCOME", "Acceptance, deadline,\nrisk tier and boundaries", NAVY),
    (2, "FREEZE t0\nEVIDENCE", "Archive only planning-time\ninputs; prevent leakage", NAVY),
    (3, "PROFILE DEMAND\nDRIVERS", "Intent, propagation, context,\nassurance and coordination", NAVY),
    (4, "FORECAST ROLE ×\nSTAGE TOUCH", "P50/P80 active service\nby required role and stage", NAVY),
    (5, "RECONCILE CAPACITY\nAND QUEUES", "Calendars, blackouts,\nallocations and existing work", NAVY),
    (6, "MODEL DELIVERY\nFLOW", "Dependencies, FIFO service,\npauses and bounded rework", NAVY),
    (7, "VERIFY EVIDENCE\nREADINESS", "Present, current, traceable\nand independently checkable", ORANGE),
    (8, "APPLY GATE\nDECISION", "Pass, conditional, fail or N/A\nwith accountable rationale", ORANGE),
    (9, "FORECAST VERIFIED\nDELIVERY", "Completion probability, items,\nbottleneck, touch, wait and block", ORANGE),
    (10, "OBSERVE AND\nRECALIBRATE", "Compare forecast with outcome;\nupdate later waves only", ORANGE),
]

TOP_X = [55, 510, 965, 1420, 1875, 2330]
TOP_Y, TOP_W, TOP_H = 310, 410, 390
BOTTOM_BOXES = [
    (55, 855, 505, 1215),
    (590, 855, 1040, 1215),
    (1655, 855, 2155, 1215),
    (2240, 855, 2740, 1215),
]
GATE_BOX = (1125, 895, 1570, 1175)


def wrapped(text: str, width: int) -> list[str]:
    result: list[str] = []
    for paragraph in text.split("\n"):
        result.extend(textwrap.wrap(paragraph, width=width) or [""])
    return result


def centered(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, text_font, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=text_font)
    draw.text((xy[0] - (box[2] - box[0]) / 2, xy[1] - (box[3] - box[1]) / 2), text, font=text_font, fill=fill)


def arrow_head(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str, size: int = 24) -> None:
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy) or 1
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    base_x, base_y = end[0] - ux * size, end[1] - uy * size
    points = [
        end,
        (int(base_x + px * size * 0.62), int(base_y + py * size * 0.62)),
        (int(base_x - px * size * 0.62), int(base_y - py * size * 0.62)),
    ]
    draw.polygon(points, fill=color)


def arrow(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], color: str = INK, width: int = 8) -> None:
    if len(points) < 2:
        raise ValueError("arrow requires at least two points")
    draw.line(points, fill=color, width=width, joint="curve")
    arrow_head(draw, points[-2], points[-1], color)


def sketch_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: str, fill: str, radius: int = 28) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=color, width=5)
    # A restrained offset stroke produces the hand-drawn/sketch-board feel.
    draw.rounded_rectangle((x1 + 3, y1 - 2, x2 - 2, y2 + 2), radius=radius + 1, outline=color, width=2)


def draw_icon(draw: ImageDraw.ImageDraw, number: int, cx: int, cy: int, color: str) -> None:
    """Small line icons; semantic, reproducible, and deliberately schematic."""
    lw = 6
    if number == 1:  # target
        for r in (54, 35, 16):
            draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=INK, width=lw)
        arrow(draw, [(cx-2, cy+2), (cx+66, cy-66)], color, 5)
    elif number == 2:  # document + lock
        draw.rounded_rectangle((cx-55, cy-65, cx+42, cy+62), radius=8, outline=INK, width=lw)
        draw.line((cx-35, cy-28, cx+20, cy-28), fill=INK, width=lw)
        draw.line((cx-35, cy-2, cx+20, cy-2), fill=INK, width=lw)
        draw.arc((cx+15, cy+5, cx+75, cy+65), 190, 350, fill=INK, width=lw)
        draw.rounded_rectangle((cx+18, cy+32, cx+72, cy+82), radius=7, outline=INK, width=lw)
    elif number == 3:  # five drivers
        for offset in (-52, -26, 0, 26, 52):
            draw.line((cx-60, cy+offset, cx+60, cy+offset), fill=INK, width=4)
            knob = cx + ((offset // 13) % 4 - 1) * 22
            draw.ellipse((knob-9, cy+offset-9, knob+9, cy+offset+9), fill=WHITE, outline=color, width=5)
    elif number == 4:  # role-stage matrix
        for i in range(3):
            for j in range(3):
                x, y = cx-62+j*45, cy-62+i*45
                draw.rounded_rectangle((x, y, x+32, y+32), radius=5, outline=INK, width=4)
        draw.ellipse((cx+34, cy+34, cx+78, cy+78), outline=color, width=6)
        draw.line((cx+56, cy+54, cx+56, cy+38), fill=color, width=4)
        draw.line((cx+56, cy+54, cx+68, cy+61), fill=color, width=4)
    elif number == 5:  # capacity and queue
        for i, h in enumerate((45, 82, 118)):
            x = cx-70+i*42
            draw.rectangle((x, cy+65-h, x+26, cy+65), outline=INK, width=5)
        for i in range(4):
            x = cx+45+i*22
            draw.ellipse((x, cy+30, x+14, cy+44), outline=color, width=4)
    elif number == 6:  # dependency flow
        nodes = [(cx-65,cy-42),(cx-10,cy-42),(cx+55,cy-42),(cx-10,cy+50),(cx+55,cy+50)]
        for a,b in ((0,1),(1,2),(1,3),(3,4)):
            arrow(draw,[nodes[a],nodes[b]],INK,4)
        for x,y in nodes:
            draw.ellipse((x-13,y-13,x+13,y+13),fill=WHITE,outline=color,width=5)
    elif number == 7:  # readiness checklist
        draw.rounded_rectangle((cx-65,cy-70,cx+65,cy+70),radius=12,outline=INK,width=lw)
        for y in (cy-38,cy,cy+38):
            draw.line((cx-42,y,cx-30,y+12,cx-10,y-12),fill=color,width=5)
            draw.line((cx+2,y,cx+43,y),fill=INK,width=5)
    elif number == 8:  # signpost
        draw.line((cx,cy-72,cx,cy+72),fill=INK,width=lw)
        for y,direction in ((cy-45,1),(cy-8,-1),(cy+29,1)):
            if direction>0:
                draw.polygon([(cx,y-14),(cx+72,y-14),(cx+91,y),(cx+72,y+14),(cx,y+14)],outline=INK,fill=WHITE)
            else:
                draw.polygon([(cx,y-14),(cx-72,y-14),(cx-91,y),(cx-72,y+14),(cx,y+14)],outline=INK,fill=WHITE)
    elif number == 9:  # completion gauge
        draw.arc((cx-75,cy-65,cx+75,cy+85),180,360,fill=INK,width=lw)
        draw.line((cx,cy+10,cx+46,cy-36),fill=color,width=7)
        draw.ellipse((cx-9,cy+1,cx+9,cy+19),fill=color)
        for i,h in enumerate((25,48,70)):
            x=cx-60+i*34
            draw.rectangle((x,cy+80-h,x+20,cy+80),outline=INK,width=4)
    else:  # learning loop
        draw.arc((cx-72,cy-72,cx+72,cy+72),25,185,fill=INK,width=lw)
        draw.arc((cx-72,cy-72,cx+72,cy+72),205,365,fill=color,width=lw)
        arrow_head(draw,(cx-58,cy-30),(cx-72,cy+4),INK,18)
        arrow_head(draw,(cx+58,cy+30),(cx+72,cy-4),color,18)
        for i,h in enumerate((30,55,82)):
            x=cx-38+i*30
            draw.rectangle((x,cy+55-h,x+18,cy+55),outline=INK,width=4)


def card(draw: ImageDraw.ImageDraw, step, box: tuple[int, int, int, int]) -> None:
    number, title, body, color = step
    x1, y1, x2, y2 = box
    fill = SOFT_BLUE if color == NAVY else SOFT_ORANGE
    sketch_box(draw, box, color, fill)
    draw.ellipse((x1+18,y1+18,x1+84,y1+84),fill=color,outline=color,width=3)
    centered(draw,(x1+51,y1+51),str(number),font(34,bold=True),WHITE)
    title_y=y1+23
    for line in title.split("\n"):
        centered(draw,((x1+x2)//2+28,title_y+22),line,font(25,heading=True),color)
        title_y+=33
    draw_icon(draw,number,(x1+x2)//2,y1+205,color)
    body_y=y2-80
    for line in body.split("\n"):
        centered(draw,((x1+x2)//2,body_y),line,font(18),MUTED)
        body_y+=27


def draw_png(path: Path) -> None:
    image=Image.new("RGB",(W,H),PAPER)
    draw=ImageDraw.Draw(image)
    centered(draw,(W/2,70),"From AI-Assisted Work to Verified Delivery",font(70,heading=True),INK)
    centered(draw,(W/2,145),"An end-to-end capacity, evidence and flow workflow for planning what can be delivered—not only what can be generated",font(27),INK)

    # Draw directional connectors beneath cards so transitions remain visually continuous.
    top_boxes=[(x,TOP_Y,x+TOP_W,TOP_Y+TOP_H) for x in TOP_X]
    bottom_boxes=BOTTOM_BOXES
    for left,right in zip(top_boxes,top_boxes[1:]):
        arrow(draw,[(left[2]+5,(left[1]+left[3])//2),(right[0]-7,(right[1]+right[3])//2)],INK,8)
    # Step 6 turns down, crosses left, and enters step 7 from above.
    six=top_boxes[-1]; seven=bottom_boxes[0]
    arrow(draw,[((six[0]+six[2])//2,six[3]+4),((six[0]+six[2])//2,770),((seven[0]+seven[2])//2,770),((seven[0]+seven[2])//2,seven[1]-8)],INK,8)
    centered(draw,(W/2,744),"DELIVERY EXECUTION TO EVIDENCE CHECKPOINT",font(21,heading=True),NAVY)
    # Main lower route: 7 -> 8 -> evidence/readiness gate -> 9 -> 10.
    lower_route=[bottom_boxes[0],bottom_boxes[1],GATE_BOX,bottom_boxes[2],bottom_boxes[3]]
    for left,right in zip(lower_route,lower_route[1:]):
        arrow(draw,[(left[2]+5,(left[1]+left[3])//2),(right[0]-7,(right[1]+right[3])//2)],INK,8)

    for step,box in zip(STEPS[:6],top_boxes):
        card(draw,step,box)
    for step,box in zip(STEPS[6:],bottom_boxes):
        card(draw,step,box)

    # The gate is on the main path—not a dangling annotation or alternate route.
    sketch_box(draw,GATE_BOX,ORANGE,WHITE,34)
    gx1,gy1,gx2,gy2=GATE_BOX
    centered(draw,((gx1+gx2)//2,gy1+48),"EVIDENCE +",font(28,heading=True),ORANGE)
    centered(draw,((gx1+gx2)//2,gy1+83),"READINESS GATE",font(28,heading=True),ORANGE)
    centered(draw,((gx1+gx2)//2,gy1+135),"PASS or CONDITIONAL",font(19,bold=True),INK)
    centered(draw,((gx1+gx2)//2,gy1+164),"continues to forecast",font(18),MUTED)
    centered(draw,((gx1+gx2)//2,gy1+205),"FAIL: rework or stop",font(18),INK)
    centered(draw,((gx1+gx2)//2,gy1+235),"N/A: document rationale",font(18),INK)

    # Complete feedback path: Step 10 → next planning wave → Step 1.
    ten=bottom_boxes[3]; one=top_boxes[0]
    arrow(draw,[(ten[2]+4,(ten[1]+ten[3])//2),(2760,(ten[1]+ten[3])//2),(2760,1572),(35,1572),(35,(one[1]+one[3])//2),(one[0]-8,(one[1]+one[3])//2)],ORANGE,7)
    centered(draw,(W/2,1540),"VERIFIED OUTCOMES FEED A LATER CALIBRATION WAVE; THE ORIGINAL t0 SNAPSHOT REMAINS IMMUTABLE",font(22,heading=True),ORANGE)

    sketch_box(draw,(300,1625,2500,1748),NAVY,SOFT_GREY,24)
    centered(draw,(W/2,1664),"CORE PRINCIPLE",font(28,heading=True),NAVY)
    centered(draw,(W/2,1710),"Plan the constrained role-stage. Keep touch, wait and block separate. Count completion only when risk-tier evidence is ready.",font(21),INK)
    centered(draw,(W/2,1772),"Conceptual workflow — not a cognitive-load measure, individual-surveillance tool, empirical result, or universal Story Point replacement",font(17),MUTED)
    image.save(path,dpi=(200,200),optimize=True)


def stext(x,y,text,size,color,weight=400,anchor="start",family="Comic Sans MS, Bradley Hand, sans-serif"):
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(text)}</text>'


def svg_arrow(points:list[tuple[int,int]],color=INK,width=8,marker="arrowBlack"):
    coords=" ".join(f"{x},{y}" for x,y in points)
    return f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#{marker})"/>'


def svg_card(step,box):
    number,title,body,color=step
    x1,y1,x2,y2=box; fill=SOFT_BLUE if color==NAVY else SOFT_ORANGE
    items=[
        f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" rx="28" fill="{fill}" stroke="{color}" stroke-width="5"/>',
        f'<rect x="{x1+3}" y="{y1-2}" width="{x2-x1-5}" height="{y2-y1+4}" rx="29" fill="none" stroke="{color}" stroke-width="2"/>',
        f'<circle cx="{x1+51}" cy="{y1+51}" r="33" fill="{color}"/>',
        stext(x1+51,y1+63,str(number),34,WHITE,700,"middle"),
    ]
    ty=y1+48
    for line in title.split("\n"):
        items.append(stext((x1+x2)//2+28,ty,line,25,color,700,"middle","Bradley Hand, Comic Sans MS, sans-serif")); ty+=34
    # Vector icon placeholder remains semantic through a numbered, labelled process card.
    items.append(f'<circle cx="{(x1+x2)//2}" cy="{y1+205}" r="58" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>')
    items.append(stext((x1+x2)//2,y1+217,{1:"OUTCOME",2:"t0",3:"PDD",4:"R×S",5:"CAP",6:"FLOW",7:"ERS",8:"GATE",9:"VDC",10:"LEARN"}[number],20,color,700,"middle"))
    by=y2-72
    for line in body.split("\n"):
        items.append(stext((x1+x2)//2,by,line,18,MUTED,400,"middle")); by+=27
    return "\n".join(items)


def draw_svg(path:Path)->None:
    top=[(x,TOP_Y,x+TOP_W,TOP_Y+TOP_H) for x in TOP_X]
    bottom=BOTTOM_BOXES
    out=[
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
        '<title id="title">From AI-Assisted Work to Verified Delivery</title>',
        '<desc id="desc">A directional ten-step workflow. Steps one through six move left to right, turn into steps seven through ten, pass through an evidence-readiness gate, and loop verified outcomes back to the next immutable planning snapshot.</desc>',
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
        f'<defs><marker id="arrowBlack" markerWidth="12" markerHeight="10" refX="10" refY="5" orient="auto"><path d="M0,0 L12,5 L0,10 z" fill="{INK}"/></marker><marker id="arrowOrange" markerWidth="12" markerHeight="10" refX="10" refY="5" orient="auto"><path d="M0,0 L12,5 L0,10 z" fill="{ORANGE}"/></marker></defs>',
        stext(W//2,95,"From AI-Assisted Work to Verified Delivery",70,INK,700,"middle","Bradley Hand, Comic Sans MS, sans-serif"),
        stext(W//2,155,"An end-to-end capacity, evidence and flow workflow for planning what can be delivered—not only what can be generated",27,INK,400,"middle"),
    ]
    for left,right in zip(top,top[1:]): out.append(svg_arrow([(left[2]+5,(left[1]+left[3])//2),(right[0]-7,(right[1]+right[3])//2)]))
    six=top[-1]; seven=bottom[0]
    out.append(svg_arrow([((six[0]+six[2])//2,six[3]+4),((six[0]+six[2])//2,770),((seven[0]+seven[2])//2,770),((seven[0]+seven[2])//2,seven[1]-8)]))
    out.append(stext(W//2,750,"DELIVERY EXECUTION TO EVIDENCE CHECKPOINT",21,NAVY,700,"middle","Bradley Hand, Comic Sans MS, sans-serif"))
    lower_route=[bottom[0],bottom[1],GATE_BOX,bottom[2],bottom[3]]
    for left,right in zip(lower_route,lower_route[1:]): out.append(svg_arrow([(left[2]+5,(left[1]+left[3])//2),(right[0]-7,(right[1]+right[3])//2)]))
    for step,box in zip(STEPS[:6],top): out.append(svg_card(step,box))
    for step,box in zip(STEPS[6:],bottom): out.append(svg_card(step,box))
    gx1,gy1,gx2,gy2=GATE_BOX
    out.extend([
        f'<rect x="{gx1}" y="{gy1}" width="{gx2-gx1}" height="{gy2-gy1}" rx="34" fill="{WHITE}" stroke="{ORANGE}" stroke-width="5"/>',
        f'<rect x="{gx1+3}" y="{gy1-2}" width="{gx2-gx1-5}" height="{gy2-gy1+4}" rx="35" fill="none" stroke="{ORANGE}" stroke-width="2"/>',
        stext((gx1+gx2)//2,gy1+56,"EVIDENCE +",28,ORANGE,700,"middle","Bradley Hand, Comic Sans MS, sans-serif"),
        stext((gx1+gx2)//2,gy1+91,"READINESS GATE",28,ORANGE,700,"middle","Bradley Hand, Comic Sans MS, sans-serif"),
        stext((gx1+gx2)//2,gy1+143,"PASS or CONDITIONAL",19,INK,700,"middle"),
        stext((gx1+gx2)//2,gy1+173,"continues to forecast",18,MUTED,400,"middle"),
        stext((gx1+gx2)//2,gy1+215,"FAIL: rework or stop",18,INK,400,"middle"),
        stext((gx1+gx2)//2,gy1+245,"N/A: document rationale",18,INK,400,"middle"),
    ])
    ten=bottom[3]; one=top[0]
    out.extend([
        svg_arrow([(ten[2]+4,(ten[1]+ten[3])//2),(2760,(ten[1]+ten[3])//2),(2760,1572),(35,1572),(35,(one[1]+one[3])//2),(one[0]-8,(one[1]+one[3])//2)],ORANGE,7,"arrowOrange"),
        stext(W//2,1550,"VERIFIED OUTCOMES FEED A LATER CALIBRATION WAVE; THE ORIGINAL t0 SNAPSHOT REMAINS IMMUTABLE",22,ORANGE,700,"middle","Bradley Hand, Comic Sans MS, sans-serif"),
        f'<rect x="300" y="1625" width="2200" height="123" rx="24" fill="{SOFT_GREY}" stroke="{NAVY}" stroke-width="5"/>',
        stext(W//2,1668,"CORE PRINCIPLE",28,NAVY,700,"middle","Bradley Hand, Comic Sans MS, sans-serif"),
        stext(W//2,1715,"Plan the constrained role-stage. Keep touch, wait and block separate. Count completion only when risk-tier evidence is ready.",21,INK,400,"middle"),
        stext(W//2,1775,"Conceptual workflow — not a cognitive-load measure, individual-surveillance tool, empirical result, or universal Story Point replacement",17,MUTED,400,"middle"),
        '</svg>',
    ])
    path.write_text("\n".join(out)+"\n",encoding="utf-8")


def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main()->None:
    OUT.mkdir(parents=True,exist_ok=True)
    png=OUT/"06-end-to-end-verified-delivery-workflow.png"
    svg=OUT/"06-end-to-end-verified-delivery-workflow.svg"
    draw_png(png); draw_svg(svg)
    manifest={
        "artifact_type":"conceptual_communication_visual",
        "empirical_result":False,
        "title":"From AI-Assisted Work to Verified Delivery",
        "style":"sketch_board_directional_workflow",
        "dimensions":{"width_px":W,"height_px":H},
        "workflow":{"step_count":10,"directional_transitions":11,"feedback_loop":True,"gate_on_main_path":True},
        "files":[{"path":png.name,"sha256":digest(png)},{"path":svg.name,"sha256":digest(svg)}],
        "interpretation_boundary":"Explanatory workflow only; not empirical evidence or a validated organizational process.",
    }
    manifest_path=OUT/"asset_manifest.json"
    manifest_path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(f"Wrote {png}\nWrote {svg}\nWrote {manifest_path}")


if __name__=="__main__":
    main()
