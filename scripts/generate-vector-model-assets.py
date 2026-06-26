#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from random import Random

import svgwrite


ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "public" / "assets" / "model_parts"
CANVAS = (512, 682)

LINE = "#2f2925"
SOFT_LINE = "#6f6258"
WHITE = "#faf7ef"

SKINS = ["#f1bd8b", "#d9915d", "#b66d45", "#f5d1ac", "#8f583b", "#e8aa73"]
HAIRS = ["#322721", "#5f3d2d", "#a35c34", "#d89447", "#dfdacd", "#22363d"]
EYES = ["#3f5f7b", "#496c48", "#6b4632", "#56406e"]

TORSOS = [
    ("#efe2c6", "#263137", "cardigan"),
    ("#d9a83f", "#fff8ea", "stripe"),
    ("#253040", "#f8f6ef", "jacket"),
    ("#61734a", "#f1ecd9", "pocket"),
    ("#f7f7f2", "#567ba6", "shirt"),
    ("#ad3a32", "#f8efe7", "track"),
    ("#515050", "#2c2b2b", "coat"),
    ("#dfd0b4", "#6f5236", "knit"),
    ("#4d7fab", "#f8f6ef", "denim"),
    ("#526f4c", "#eee6d4", "stripe"),
    ("#242426", "#f5f4ee", "rider"),
    ("#73767c", "#2c2c2d", "blazer"),
    ("#c6a577", "#563e2f", "trench"),
    ("#eee1ca", "#775c48", "crop"),
    ("#a0c0d9", "#f6f8f9", "shirt"),
    ("#f0e8dc", "#514941", "linen"),
    ("#b26f35", "#f7efe1", "suede"),
    ("#474c54", "#f6f4ef", "blazer"),
    ("#c99436", "#2b4b6e", "varsity"),
    ("#30393c", "#ebeeee", "wind"),
    ("#285d61", "#f7f2e3", "camp"),
    ("#c45735", "#f4efe7", "overshirt"),
    ("#252a30", "#51565a", "hoodie"),
    ("#78472e", "#f4ecde", "leather"),
]

LEGS = [
    ("#242b38", "#f2f2ee", "pants"),
    ("#33538f", "#faf7ee", "skirt"),
    ("#5794c4", "#fafaf7", "shorts"),
    ("#292b32", "#1e2024", "boots"),
    ("#b7bcc3", "#f4f4f0", "jogger"),
    ("#353036", "#eeece1", "skirt"),
    ("#25334c", "#f0f0ea", "crop"),
    ("#b9965c", "#303230", "cargo"),
    ("#4778a8", "#f6f6f2", "wide"),
    ("#2a2b2f", "#f5f4ef", "shorts"),
    ("#625f64", "#f2f1ea", "skirt"),
    ("#435941", "#553b27", "pants"),
    ("#579ccf", "#242222", "shorts"),
    ("#ece8da", "#2d2925", "cargo"),
    ("#202126", "#efeee7", "skirt"),
    ("#64acd8", "#f8f7f2", "cargo"),
    ("#2b4d70", "#f0f1ee", "pants"),
    ("#27292f", "#f5f5ef", "jogger"),
    ("#a92d31", "#1f2024", "skirt"),
    ("#24272b", "#232326", "boots"),
    ("#eedcba", "#5d402f", "skirt"),
    ("#1f2226", "#f2f2ed", "wide"),
    ("#89bee2", "#f8f8f4", "ripped"),
    ("#2d4366", "#f0eee8", "shorts"),
]


@dataclass(frozen=True)
class Part:
    folder: str
    prefix: str


PARTS = {
    "head": Part("heads", "head_"),
    "arms": Part("arms", "arms_"),
    "torso": Part("torsos", "torso_"),
    "legs": Part("legs", "legs_"),
}


def drawing(path: Path) -> svgwrite.Drawing:
    return svgwrite.Drawing(str(path), size=CANVAS, viewBox=f"0 0 {CANVAS[0]} {CANVAS[1]}", profile="full")


def attrs(fill: str, stroke: str = LINE, width: float = 3, **extra):
    return {"fill": fill, "stroke": stroke, "stroke_width": width, "stroke_linejoin": "round", "stroke_linecap": "round", **extra}


def darker(hex_color: str, amount: int = 24) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"#{max(0, r - amount):02x}{max(0, g - amount):02x}{max(0, b - amount):02x}"


def lighter(hex_color: str, amount: int = 24) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"#{min(255, r + amount):02x}{min(255, g + amount):02x}{min(255, b + amount):02x}"


def add_limb(dwg: svgwrite.Drawing, points: list[tuple[float, float]], color: str, width: float):
    dwg.add(dwg.polyline(points=points, fill="none", stroke=darker(color, 28), stroke_width=width + 7, stroke_linecap="round", stroke_linejoin="round"))
    dwg.add(dwg.polyline(points=points, fill="none", stroke=color, stroke_width=width, stroke_linecap="round", stroke_linejoin="round"))


def draw_head(path: Path, index: int):
    rng = Random(7100 + index)
    dwg = drawing(path)
    skin = SKINS[index % len(SKINS)]
    hair = HAIRS[(index * 2 + index // 4) % len(HAIRS)]
    eye = EYES[index % len(EYES)]
    cx = 256 + rng.randint(-3, 3)
    top = 76 + rng.randint(-2, 4)
    face_w = 104 + rng.randint(-8, 10)
    face_h = 132 + rng.randint(-6, 8)

    dwg.add(dwg.rect(insert=(cx - 20, top + face_h - 6), size=(40, 48), rx=12, **attrs(darker(skin, 8), SOFT_LINE, 2)))
    dwg.add(dwg.ellipse(center=(cx, top + face_h / 2), r=(face_w / 2, face_h / 2), **attrs(skin, LINE, 3)))
    dwg.add(dwg.ellipse(center=(cx - face_w / 2 - 4, top + 70), r=(12, 16), **attrs(skin, SOFT_LINE, 2)))
    dwg.add(dwg.ellipse(center=(cx + face_w / 2 + 4, top + 70), r=(12, 16), **attrs(skin, SOFT_LINE, 2)))

    hair_style = index % 6
    if hair_style == 0:
        dwg.add(dwg.path(d=f"M {cx-face_w/2-20} {top+32} Q {cx} {top-36} {cx+face_w/2+20} {top+32} L {cx+face_w/2+16} {top+70} Q {cx} {top+30} {cx-face_w/2-16} {top+70} Z", **attrs(hair, LINE, 3)))
    elif hair_style == 1:
        dwg.add(dwg.rect(insert=(cx - face_w / 2 - 13, top - 18), size=(face_w + 26, 72), rx=28, **attrs(hair, LINE, 3)))
        dwg.add(dwg.rect(insert=(cx - face_w / 2 - 10, top + 30), size=(face_w + 20, 34), **attrs(hair, hair, 1)))
    elif hair_style == 2:
        for n in range(8):
            x = cx - 58 + n * 16
            dwg.add(dwg.ellipse(center=(x, top + 6 + abs(n - 3.5) * 6), r=(24, 22), **attrs(hair, LINE, 2)))
    elif hair_style == 3:
        dwg.add(dwg.ellipse(center=(cx, top + 16), r=(face_w / 2 + 16, 50), **attrs(hair, LINE, 3)))
        dwg.add(dwg.path(d=f"M {cx-12} {top-18} L {cx+2} {top-52} L {cx+18} {top-10} Z", **attrs(hair, LINE, 2)))
    elif hair_style == 4:
        dwg.add(dwg.ellipse(center=(cx, top + 12), r=(face_w / 2 + 20, 48), **attrs(hair, LINE, 3)))
        for side in (-1, 1):
            dwg.add(dwg.path(d=f"M {cx+side*46} {top+34} Q {cx+side*70} {top+92} {cx+side*48} {top+138}", fill="none", stroke=hair, stroke_width=18, stroke_linecap="round"))
    else:
        dwg.add(dwg.path(d=f"M {cx-face_w/2-16} {top+28} Q {cx} {top-30} {cx+face_w/2+16} {top+28} L {cx+face_w/2+10} {top+78} Q {cx} {top+50} {cx-face_w/2-10} {top+78} Z", **attrs(hair, LINE, 3)))

    for n in range(5 + index % 3):
        x = cx - face_w / 2 + 14 + n * (face_w - 28) / max(1, 4 + index % 3)
        dwg.add(dwg.path(d=f"M {x-8} {top+12} L {x+9} {top+12} L {x+rng.randint(-16,16)} {top+70+rng.randint(-8,9)} Z", **attrs(hair, darker(hair, 28), 1.5)))

    for side in (-1, 1):
        ex = cx + side * 28
        dwg.add(dwg.ellipse(center=(ex, top + 76), r=(17, 10), **attrs(WHITE, LINE, 2)))
        dwg.add(dwg.circle(center=(ex + side * 2, top + 77), r=5, fill=eye, stroke=LINE, stroke_width=1.2))
        dwg.add(dwg.path(d=f"M {ex-side*18} {top+62} Q {ex} {top+55} {ex+side*19} {top+62}", fill="none", stroke=LINE, stroke_width=3, stroke_linecap="round"))
    dwg.add(dwg.path(d=f"M {cx} {top+88} L {cx-4} {top+107} L {cx+4} {top+107}", fill="none", stroke=darker(skin, 42), stroke_width=2, stroke_linejoin="round"))
    dwg.add(dwg.path(d=f"M {cx-18} {top+122} Q {cx} {top+132} {cx+20} {top+122}", fill="none", stroke="#7a423c", stroke_width=2.4, stroke_linecap="round"))
    if index % 3 == 0:
        for side in (-1, 1):
            dwg.add(dwg.ellipse(center=(cx + side * (face_w / 2 + 17), top + 108), r=(5, 10), fill="#c99a42", stroke=LINE, stroke_width=2))
    dwg.save()


def arm_pose(index: int):
    pose = index % 8
    if pose == 0:
        return [(151, 240), (133, 330), (137, 430)], [(361, 240), (379, 330), (375, 430)]
    if pose == 1:
        return [(151, 242), (123, 314), (101, 372)], [(361, 242), (389, 314), (411, 372)]
    if pose == 2:
        return [(151, 252), (200, 323), (235, 343)], [(361, 252), (312, 323), (277, 343)]
    if pose == 3:
        return [(151, 242), (133, 314), (156, 384)], [(361, 242), (385, 310), (370, 396)]
    if pose == 4:
        return [(151, 240), (126, 295), (110, 356)], [(361, 240), (386, 295), (402, 356)]
    if pose == 5:
        return [(151, 246), (190, 309), (230, 392)], [(361, 246), (322, 309), (282, 392)]
    if pose == 6:
        return [(151, 240), (124, 323), (120, 407)], [(361, 240), (388, 323), (392, 407)]
    return [(151, 240), (112, 302), (88, 332)], [(361, 240), (400, 302), (424, 332)]


def draw_arms(path: Path, index: int):
    dwg = drawing(path)
    skin = SKINS[(index * 3 + 1) % len(SKINS)]
    left, right = arm_pose(index)
    for pts in (left, right):
        add_limb(dwg, pts, skin, 20)
        hx, hy = pts[-1]
        dwg.add(dwg.ellipse(center=(hx, hy), r=(13, 15), **attrs(skin, LINE, 2)))
        for n in range(4):
            dx = (n - 1.5) * 5
            dwg.add(dwg.line(start=(hx + dx, hy + 10), end=(hx + dx + (n - 1.5) * 2, hy + 23), stroke=darker(skin, 10), stroke_width=3, stroke_linecap="round"))
    if index % 4 == 1:
        hx, hy = right[-1]
        dwg.add(dwg.line(start=(hx - 8, hy - 10), end=(hx - 20, hy - 42), stroke=skin, stroke_width=5, stroke_linecap="round"))
        dwg.add(dwg.line(start=(hx + 2, hy - 12), end=(hx + 1, hy - 46), stroke=skin, stroke_width=5, stroke_linecap="round"))
    dwg.save()


def draw_torso(path: Path, index: int):
    dwg = drawing(path)
    primary, secondary, style = TORSOS[index]
    cx = 256
    top = 224
    bottom = 430
    shoulder = 174 + (index % 4) * 6
    waist = 126 + (index % 5) * 5
    body = [(cx - shoulder / 2, top + 16), (cx + shoulder / 2, top + 16), (cx + waist / 2, bottom), (cx - waist / 2, bottom)]
    dwg.add(dwg.polygon(points=body, **attrs(primary, LINE, 4)))
    dwg.add(dwg.polygon(points=[(cx - 44, top), (cx + 44, top), (cx + 34, top + 38), (cx - 34, top + 38)], **attrs(secondary, LINE, 2)))
    dwg.add(dwg.path(d=f"M {cx-31} {top+10} L {cx} {top+76} L {cx+31} {top+10}", fill=secondary, stroke=SOFT_LINE, stroke_width=2, stroke_linejoin="round"))
    dwg.add(dwg.line(start=(cx, top + 33), end=(cx, bottom - 9), stroke=darker(primary, 40), stroke_width=3, stroke_linecap="round"))
    for side in (-1, 1):
        sleeve = [(cx + side * shoulder / 2, top + 18), (cx + side * (shoulder / 2 + 25), top + 78), (cx + side * (waist / 2 + 20), top + 170), (cx + side * waist / 2, bottom - 16)]
        dwg.add(dwg.polygon(points=sleeve, **attrs(darker(primary, 8), LINE, 3)))

    if style in ("jacket", "cardigan", "rider", "blazer", "trench", "leather"):
        dwg.add(dwg.polygon(points=[(cx - 82, top + 22), (cx - 28, top + 17), (cx - 18, bottom - 8), (cx - 62, bottom - 12)], **attrs(darker(primary, 18), LINE, 2.5)))
        dwg.add(dwg.polygon(points=[(cx + 82, top + 22), (cx + 28, top + 17), (cx + 18, bottom - 8), (cx + 62, bottom - 12)], **attrs(darker(primary, 18), LINE, 2.5)))
    if style in ("stripe", "wind"):
        for y in range(top + 54, bottom - 25, 29):
            dwg.add(dwg.line(start=(cx - 78, y), end=(cx + 78, y), stroke=secondary, stroke_width=7, stroke_linecap="round"))
    if style in ("pocket", "denim", "camp"):
        for side in (-1, 1):
            dwg.add(dwg.rect(insert=(cx + side * 28 - 18, top + 86), size=(36, 34), rx=5, fill=darker(primary, 16), stroke=LINE, stroke_width=2))
    if style in ("track", "varsity"):
        dwg.add(dwg.line(start=(cx - 80, top + 54), end=(cx + 80, top + 54), stroke=WHITE, stroke_width=7, stroke_linecap="round"))
        dwg.add(dwg.line(start=(cx - 84, top + 82), end=(cx + 84, top + 82), stroke=WHITE, stroke_width=4, stroke_linecap="round"))
    if style in ("knit", "linen"):
        for x in range(cx - 65, cx + 66, 24):
            dwg.add(dwg.line(start=(x, top + 36), end=(x + 14, bottom - 18), stroke=lighter(primary, 24), stroke_width=2, stroke_linecap="round"))
    if style == "hoodie":
        dwg.add(dwg.path(d=f"M {cx-42} {top+18} Q {cx} {top-10} {cx+42} {top+18}", fill="none", stroke=secondary, stroke_width=10, stroke_linecap="round"))
    for y in range(top + 80, bottom - 22, 35):
        dwg.add(dwg.circle(center=(cx + 7, y), r=4, fill=darker(primary, 60), stroke=LINE, stroke_width=1))
    dwg.save()


def draw_legs(path: Path, index: int):
    dwg = drawing(path)
    primary, secondary, style = LEGS[index]
    skin = SKINS[(index * 2 + 3) % len(SKINS)]
    cx = 256
    waist_y = 392
    shoe_y = 640
    dwg.add(dwg.rect(insert=(cx - 75, waist_y - 8), size=(150, 24), rx=7, **attrs(darker(primary, 18), LINE, 2)))

    if style == "skirt":
        skirt_w = 150 + (index % 4) * 8
        skirt_h = 82 + (index % 3) * 9
        dwg.add(dwg.polygon(points=[(cx - skirt_w / 2, waist_y), (cx + skirt_w / 2, waist_y), (cx + skirt_w / 2 - 16, waist_y + skirt_h), (cx - skirt_w / 2 + 16, waist_y + skirt_h)], **attrs(primary, LINE, 3)))
        for x in range(round(cx - skirt_w / 2 + 20), round(cx + skirt_w / 2 - 12), 23):
            dwg.add(dwg.line(start=(x, waist_y + 6), end=(x + 7, waist_y + skirt_h - 6), stroke=darker(primary, 35), stroke_width=2))
        leg_top = waist_y + skirt_h - 4
        for side in (-1, 1):
            x = cx + side * 34
            dwg.add(dwg.rect(insert=(x - 16, leg_top), size=(32, shoe_y - 32 - leg_top), rx=13, **attrs(skin, LINE, 2)))
    elif style == "shorts":
        for side in (-1, 1):
            x = cx + side * 39
            dwg.add(dwg.rect(insert=(x - 34, waist_y), size=(68, 83), rx=10, **attrs(primary, LINE, 3)))
            dwg.add(dwg.rect(insert=(x - 16, waist_y + 78), size=(32, shoe_y - 32 - (waist_y + 78)), rx=13, **attrs(skin, LINE, 2)))
    else:
        wide = style in ("wide", "cargo", "jogger")
        leg_top_w = 54 if wide else 42
        leg_bottom_w = 47 if wide else 31
        for side in (-1, 1):
            x = cx + side * 34
            dwg.add(dwg.polygon(points=[(x - leg_top_w / 2, waist_y), (x + leg_top_w / 2, waist_y), (x + leg_bottom_w / 2, shoe_y - 22), (x - leg_bottom_w / 2, shoe_y - 22)], **attrs(primary, LINE, 3)))
            dwg.add(dwg.line(start=(x + side * 7, waist_y + 26), end=(x + side * 12, shoe_y - 38), stroke=darker(primary, 36), stroke_width=2))
        dwg.add(dwg.line(start=(cx, waist_y + 8), end=(cx, shoe_y - 35), stroke=darker(primary, 52), stroke_width=3))
        if style == "ripped":
            for side in (-1, 1):
                x = cx + side * 34
                dwg.add(dwg.path(d=f"M {x-16} {waist_y+98} Q {x} {waist_y+86} {x+16} {waist_y+98}", fill="none", stroke=WHITE, stroke_width=5, stroke_linecap="round"))
    for side in (-1, 1):
        x = cx + side * 42
        shoe_color = secondary
        dwg.add(dwg.ellipse(center=(x, shoe_y - 12), r=(35, 15), **attrs(shoe_color, LINE, 3)))
        dwg.add(dwg.line(start=(x - 26, shoe_y - 12), end=(x + 27, shoe_y - 12), stroke=WHITE, stroke_width=3, stroke_linecap="round"))
    dwg.save()


DRAWERS = {"head": draw_head, "arms": draw_arms, "torso": draw_torso, "legs": draw_legs}


def generate():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for part, spec in PARTS.items():
        folder = OUT_ROOT / spec.folder
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.glob("*.svg"):
            old.unlink()
        for index in range(24):
            DRAWERS[part](folder / f"{spec.prefix}{index}.svg", index)
        print(f"{part}: 24")


if __name__ == "__main__":
    generate()
