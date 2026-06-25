#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import random
from dataclasses import dataclass
from pathlib import Path

from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "output/imagegen/character-parts"
PUBLIC_ROOT = ROOT / "public/assets"

MODEL = "HiDream-ai/HiDream-I1-Full"
PROVIDER = "fal-ai"
KEY_COLOR = "#00ff00"

FACE_SOURCE_SIZE = (1024, 1024)
BODY_SOURCE_SIZE = (1024, 1536)
FACE_PUBLIC_SIZE = (512, 512)
BODY_PUBLIC_SIZE = (512, 768)

NEGATIVE_PROMPT = (
    "text, watermark, logo, signature, artist mark, red seal, stamp, calligraphy, "
    "letters, numbers, symbols, border, ui, frame, photorealism, 3d render, vector art, "
    "flat svg, fashion outfit, clothes variation, costume, buttons, patterns, printed graphics, "
    "nudity, exposed private parts, explicit anatomy, horror, weapon, existing character, franchise"
)

BASE_STYLE = (
    "Original game asset, hand-painted pastoral animated feature influence, "
    "watercolor and gouache texture, soft ink detail, warm natural palette, gentle paper grain. "
    "Do not copy any specific living artist, studio, franchise, or existing character. "
    f"Perfectly flat solid {KEY_COLOR} chroma-key background only. "
    "The background must be one uniform color with no shadow, no gradient, no texture, no floor, "
    "no stamp, no writing, no logo, no watermark. "
)


@dataclass(frozen=True)
class Asset:
    file: str
    label: str
    prompt: str
    seed: int


FACE_ASSETS = [
    Asset("face-01.png", "둥근 볼·초승달 눈", "round face, plump cheeks, crescent smiling eyes, tiny calm mouth", 21001),
    Asset("face-02.png", "긴 타원·가는 눈썹", "long oval face, thin eyebrows, quiet narrow eyes, slim chin", 21002),
    Asset("face-03.png", "사각 턱·짙은 눈썹", "square jaw, thick eyebrows, compact nose, confident warm eyes", 21003),
    Asset("face-04.png", "하트형 이마·작은 입", "heart-shaped forehead, small mouth, narrow chin, soft attentive eyes", 21004),
    Asset("face-05.png", "넓은 광대·맑은 눈", "wide cheekbones, clear round eyes, gentle broad nose, relaxed mouth", 21005),
    Asset("face-06.png", "좁은 얼굴·처진 눈", "narrow face, drooping sleepy eyes, long nose, mild tired mouth", 21006),
    Asset("face-07.png", "납작 얼굴·넓은 미간", "flat wide face, wide-set eyes, short nose, simple straight brows", 21007),
    Asset("face-08.png", "다이아몬드형·뾰족 턱", "diamond-shaped face, pointed chin, sharp cheek planes, curious eyes", 21008),
    Asset("face-09.png", "작은 코·큰 귀", "small nose, large rounded ears, open soft eyes, rounded chin", 21009),
    Asset("face-10.png", "긴 코·깊은 눈", "long nose, deep-set eyes, long cheeks, thoughtful restrained mouth", 21010),
    Asset("face-11.png", "주근깨·둥근 눈", "freckles, round bright eyes, soft cheeks, small friendly smile", 21011),
    Asset("face-12.png", "반쯤 감은 눈·잠잠한 입", "half-closed eyes, quiet straight mouth, soft eyelids, low brows", 21012),
    Asset("face-13.png", "통통한 볼·작은 눈", "very plump cheeks, small eyes, tiny nose, mellow expression", 21013),
    Asset("face-14.png", "길쭉한 코·얇은 입", "elongated nose, thin mouth, long face, delicate ears", 21014),
    Asset("face-15.png", "큰 눈·짧은 턱", "large eyes, short chin, small rounded nose, open surprised expression", 21015),
    Asset("face-16.png", "굵은 눈썹·넓은 턱", "bold eyebrows, broad jaw, strong cheeks, kind steady eyes", 21016),
    Asset("face-17.png", "물방울 얼굴·높은 이마", "teardrop face, high forehead, small chin, gentle small eyes", 21017),
    Asset("face-18.png", "비대칭 눈썹·작은 턱", "asymmetric eyebrows, tiny chin, offbeat curious expression, uneven eyes", 21018),
    Asset("face-19.png", "곱슬 앞머리·둥근 얼굴", "round face with curly fringe, soft cheeks, lively eyes, warm grin", 21019),
    Asset("face-20.png", "민머리·매끈한 이마", "smooth bald head, clean forehead, mild eyes, simple calm mouth", 21020),
    Asset("face-21.png", "내려간 눈꼬리·긴 턱", "downturned eyes, long chin, narrow cheeks, sympathetic expression", 21021),
    Asset("face-22.png", "올라간 눈꼬리·짧은 코", "upturned eyes, short nose, neat brows, playful compact mouth", 21022),
    Asset("face-23.png", "넓은 코·넉넉한 입", "wide nose, generous mouth, broad cheeks, cheerful steady eyes", 21023),
    Asset("face-24.png", "작은 귀·가는 얼굴", "small ears, slim face, delicate nose, quiet observant eyes", 21024),
    Asset("face-25.png", "둥근 턱·도톰한 입술", "rounded chin, full soft lips, gentle eyelids, warm cheeks", 21025),
    Asset("face-26.png", "날카로운 코·가는 턱", "sharp nose, slender chin, precise eyes, angular cheeks", 21026),
    Asset("face-27.png", "낮은 이마·짙은 속눈썹", "low forehead, dark lashes, compact round face, shy expression", 21027),
    Asset("face-28.png", "큰 이마·작은 눈동자", "large forehead, tiny pupils, narrow mouth, thoughtful odd expression", 21028),
    Asset("face-29.png", "말랑한 얼굴·낮은 코", "soft squishy face, low nose bridge, round cheeks, relaxed tiny smile", 21029),
    Asset("face-30.png", "엄숙한 얼굴·반듯한 눈썹", "solemn face, straight eyebrows, centered gaze, small firm mouth", 21030),
    Asset("face-31.png", "기묘한 미소·비뚤어진 코", "quirky smile, slightly crooked nose, uneven cheeks, clever eyes", 21031),
    Asset("face-32.png", "조용한 얼굴·가느다란 입", "quiet face, thin mouth, soft narrow eyes, delicate chin", 21032),
]

BODY_ASSETS = [
    Asset("body-01.png", "작고 둥근 몸", "small rounded full body, compact torso, short relaxed limbs", 31001),
    Asset("body-02.png", "길고 마른 몸", "tall skinny full body, long narrow torso, thin limbs", 31002),
    Asset("body-03.png", "넓고 튼튼한 몸", "broad sturdy full body, wide chest, strong short limbs", 31003),
    Asset("body-04.png", "말랑한 배 몸", "soft belly full body, rounded middle, gentle shoulders", 31004),
    Asset("body-05.png", "짧은 다리 몸", "full body with short legs, low center of gravity, compact stance", 31005),
    Asset("body-06.png", "긴 다리 몸", "full body with long legs, high waist, balanced narrow torso", 31006),
    Asset("body-07.png", "긴 팔 몸", "full body with long arms, relaxed hands near knees, narrow frame", 31007),
    Asset("body-08.png", "짧은 팔 몸", "full body with short arms, rounded shoulders, compact hands", 31008),
    Asset("body-09.png", "좁은 어깨 몸", "full body with narrow shoulders, slim chest, careful small stance", 31009),
    Asset("body-10.png", "넓은 어깨 몸", "full body with wide shoulders, tapered waist, steady stance", 31010),
    Asset("body-11.png", "굽은 등 몸", "full body with slightly curved back, gentle forward posture", 31011),
    Asset("body-12.png", "곧은 자세 몸", "full body with upright posture, straight spine, even stance", 31012),
    Asset("body-13.png", "큰 손·큰 발 몸", "full body with large hands and large feet, sturdy grounded limbs", 31013),
    Asset("body-14.png", "작은 손·작은 발 몸", "full body with small hands and small feet, delicate compact limbs", 31014),
    Asset("body-15.png", "휘어진 다리 몸", "full body with gently bowed legs, offbeat friendly stance", 31015),
    Asset("body-16.png", "균형 잡힌 보통 몸", "balanced ordinary full body, medium torso, medium arms and legs", 31016),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate face and body assets with Hugging Face.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing assets.")
    parser.add_argument("--model", default=MODEL, help="Hugging Face text-to-image model id.")
    parser.add_argument("--provider", default=PROVIDER, help="Hugging Face inference provider.")
    parser.add_argument("--kind", choices=["all", "face", "body"], default="all")
    parser.add_argument("--only", nargs="*", help="Generate only these output filenames.")
    parser.add_argument("--seed-offset", type=int, default=0, help="Add an offset when retrying generation.")
    parser.add_argument("--steps", type=int, default=30, help="Inference steps for expensive final generation.")
    parser.add_argument("--token-file", type=Path, help="Read the Hugging Face token from this file.")
    parser.add_argument("--reprocess", action="store_true", help="Rebuild public PNGs from existing raw outputs.")
    parser.add_argument("--local-fallback", action="store_true", help="Create deterministic local raster PNGs without API calls.")
    return parser.parse_args()


def clean_token(token: str | None) -> str:
    return (token or "").strip().strip("'\"")


def token_from_env(token_file: Path | None = None) -> str:
    token = clean_token(token_file.read_text() if token_file else None)
    token = token or clean_token(os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN"))
    if not token:
        raise SystemExit("Set HF_TOKEN or pass --token-file before running this script.")
    return token


def target_sets(kind: str) -> list[tuple[str, list[Asset], tuple[int, int], tuple[int, int]]]:
    sets = [
        ("faces", FACE_ASSETS, FACE_SOURCE_SIZE, FACE_PUBLIC_SIZE),
        ("bodies", BODY_ASSETS, BODY_SOURCE_SIZE, BODY_PUBLIC_SIZE),
    ]
    if kind == "face":
        return [sets[0]]
    if kind == "body":
        return [sets[1]]
    return sets


def generate_asset(
    client: InferenceClient,
    asset: Asset,
    model: str,
    size: tuple[int, int],
    steps: int,
    seed_offset: int,
    group: str,
) -> Image.Image:
    if group == "faces":
        prompt = (
            f"{BASE_STYLE} Head-only character face sprite, no neck, no shoulders, no body, no clothes. "
            f"Centered head, transparent-ready clean silhouette, large readable facial features. {asset.prompt}."
        )
    else:
        prompt = (
            f"{BASE_STYLE} Headless neutral body sprite from neck to feet. No head, no face, no hair. "
            "No outfit, no fashion details. Fully modest smooth neutral base form, "
            "no exposed anatomy details. Body shape only. Centered standing pose, hands and feet visible. "
            f"{asset.prompt}."
        )

    return client.text_to_image(
        prompt,
        model=model,
        negative_prompt=NEGATIVE_PROMPT,
        width=size[0],
        height=size[1],
        num_inference_steps=steps,
        guidance_scale=5.0,
        seed=asset.seed + seed_offset,
    )


def color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def likely_key_green(r: int, g: int, b: int) -> bool:
    return g > 115 and g - max(r, b) > 24


def likely_plain_background(r: int, g: int, b: int) -> bool:
    if likely_key_green(r, g, b):
        return True
    if min(r, g, b) > 235 and max(r, g, b) - min(r, g, b) < 32:
        return True
    return False


def remove_background(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size

    visited = bytearray(width * height)
    queue: list[tuple[int, int]] = []

    def push(x: int, y: int) -> None:
        index = y * width + x
        if visited[index]:
            return
        visited[index] = 1
        queue.append((x, y))

    for x in range(width):
        push(x, 0)
        push(x, height - 1)
    for y in range(height):
        push(0, y)
        push(width - 1, y)

    background = bytearray(width * height)
    while queue:
        x, y = queue.pop()
        r, g, b, _ = pixels[x, y]
        background[y * width + x] = 1
        current = (r, g, b)

        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nx < 0 or ny < 0 or nx >= width or ny >= height:
                continue
            index = ny * width + nx
            if visited[index]:
                continue
            nr, ng, nb, _ = pixels[nx, ny]
            neighbor = (nr, ng, nb)
            if likely_plain_background(nr, ng, nb) and color_distance(current, neighbor) < 94:
                visited[index] = 1
                queue.append((nx, ny))

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if background[y * width + x]:
                pixels[x, y] = (r, g, b, 0)
                continue
            green_score = g - max(r, b)
            if g > 150 and green_score > 45:
                alpha = 0 if g > 175 and green_score > 70 else 80
                pixels[x, y] = (r, min(g, max(r, b) + 12), b, alpha)
            elif green_score > 25 and g > 120:
                pixels[x, y] = (r, min(g, max(r, b) + 18), b, a)
    return rgba


def clear_face_lower_area(image: Image.Image) -> Image.Image:
    pixels = image.load()
    width, height = image.size
    cutoff = int(height * 0.76)
    fade = max(1, int(height * 0.05))
    for y in range(cutoff, height):
        factor = max(0, 1 - ((y - cutoff) / fade))
        for x in range(width):
            r, g, b, a = pixels[x, y]
            pixels[x, y] = (r, g, b, int(a * factor))
    return image


def clear_body_floor_area(image: Image.Image) -> Image.Image:
    pixels = image.load()
    width, height = image.size
    floor_top = int(height * 0.68)
    visited = bytearray(width * height)
    queue: list[tuple[int, int]] = []

    def push(x: int, y: int) -> None:
        if y < floor_top:
            return
        index = y * width + x
        if visited[index]:
            return
        visited[index] = 1
        queue.append((x, y))

    for x in range(width):
        push(x, height - 1)
    for y in range(floor_top, height):
        push(0, y)
        push(width - 1, y)

    while queue:
        x, y = queue.pop()
        r, g, b, a = pixels[x, y]
        if a == 0:
            pixels[x, y] = (r, g, b, 0)
        else:
            pixels[x, y] = (r, g, b, 0)
        current = (r, g, b)
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nx < 0 or ny < floor_top or nx >= width or ny >= height:
                continue
            index = ny * width + nx
            if visited[index]:
                continue
            nr, ng, nb, na = pixels[nx, ny]
            if na == 0 or likely_key_green(nr, ng, nb) or color_distance(current, (nr, ng, nb)) < 72:
                visited[index] = 1
                queue.append((nx, ny))

    return image


def save_public_copy(source: Image.Image, public_path: Path, size: tuple[int, int], group: str) -> None:
    alpha = remove_background(source)
    fitted = ImageOps.contain(alpha, size, method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (255, 255, 255, 0))
    canvas.alpha_composite(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
    if group == "faces":
        canvas = clear_face_lower_area(canvas)
    if group == "bodies":
        canvas = clear_body_floor_area(canvas)
    canvas.save(public_path, format="PNG", optimize=True)


def save_contact_sheet() -> None:
    faces = [Image.open(PUBLIC_ROOT / "faces" / asset.file).convert("RGBA") for asset in FACE_ASSETS if (PUBLIC_ROOT / "faces" / asset.file).exists()]
    bodies = [Image.open(PUBLIC_ROOT / "bodies" / asset.file).convert("RGBA") for asset in BODY_ASSETS if (PUBLIC_ROOT / "bodies" / asset.file).exists()]
    if not faces or not bodies:
        return

    face_cell = (160, 160)
    body_cell = (128, 192)
    face_sheet = Image.new("RGBA", (face_cell[0] * 8, face_cell[1] * 4), (246, 236, 214, 255))
    for index, face in enumerate(faces[:32]):
        thumb = ImageOps.contain(face, (138, 138), method=Image.Resampling.LANCZOS)
        x = (index % 8) * face_cell[0] + (face_cell[0] - thumb.width) // 2
        y = (index // 8) * face_cell[1] + (face_cell[1] - thumb.height) // 2
        face_sheet.alpha_composite(thumb, (x, y))

    body_sheet = Image.new("RGBA", (body_cell[0] * 8, body_cell[1] * 2), (246, 236, 214, 255))
    for index, body in enumerate(bodies[:16]):
        thumb = ImageOps.contain(body, (112, 176), method=Image.Resampling.LANCZOS)
        x = (index % 8) * body_cell[0] + (body_cell[0] - thumb.width) // 2
        y = (index // 8) * body_cell[1] + (body_cell[1] - thumb.height) // 2
        body_sheet.alpha_composite(thumb, (x, y))

    out = Image.new("RGBA", (face_sheet.width, face_sheet.height + body_sheet.height), (246, 236, 214, 255))
    out.alpha_composite(face_sheet, (0, 0))
    out.alpha_composite(body_sheet, (0, face_sheet.height))
    out.convert("RGB").save(PUBLIC_ROOT / "character-contact-sheet.png", format="PNG", optimize=True)


def save_icons() -> None:
    face_path = PUBLIC_ROOT / "faces/face-19.png"
    body_path = PUBLIC_ROOT / "bodies/body-16.png"
    if not face_path.exists() or not body_path.exists():
        return

    canvas = Image.new("RGBA", (1024, 1024), (238, 217, 178, 255))
    body = Image.open(body_path).convert("RGBA")
    face = Image.open(face_path).convert("RGBA")
    body = ImageOps.contain(body, (590, 884), method=Image.Resampling.LANCZOS)
    face = ImageOps.contain(face, (380, 380), method=Image.Resampling.LANCZOS)
    canvas.alpha_composite(body, ((1024 - body.width) // 2, 92))
    canvas.alpha_composite(face, ((1024 - face.width) // 2, 82))

    for size, filename in ((192, "icon-192.png"), (512, "icon-512.png"), (180, "apple-icon.png")):
        icon = canvas.resize((size, size), Image.Resampling.LANCZOS)
        icon.save(ROOT / f"public/{filename}", format="PNG", optimize=True)


def jitter_box(box: tuple[int, int, int, int], rng: random.Random, amount: int) -> tuple[int, int, int, int]:
    return tuple(value + rng.randint(-amount, amount) for value in box)  # type: ignore[return-value]


def paint_ellipse(
    image: Image.Image,
    box: tuple[int, int, int, int],
    fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int],
    rng: random.Random,
    width: int = 5,
) -> None:
    layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(layer)
    for _ in range(16):
        draw.ellipse(jitter_box(box, rng, 10), fill=(fill[0], fill[1], fill[2], max(10, fill[3] // 4)))
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    image.alpha_composite(layer)
    draw = ImageDraw.Draw(image)
    draw.ellipse(box, outline=outline, width=width)


def paint_line(
    image: Image.Image,
    points: list[tuple[int, int]],
    fill: tuple[int, int, int, int],
    rng: random.Random,
    width: int,
) -> None:
    draw = ImageDraw.Draw(image)
    for offset in (-1, 0, 1):
        shifted = [(x + rng.randint(-2, 2), y + offset + rng.randint(-2, 2)) for x, y in points]
        draw.line(shifted, fill=fill, width=width, joint="curve")


def draw_local_face(asset: Asset, index: int) -> Image.Image:
    rng = random.Random(asset.seed)
    image = Image.new("RGBA", FACE_SOURCE_SIZE, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    face_w = 520 + (index % 5) * 34 - (index % 3) * 18
    face_h = 500 + (index % 7) * 26
    cx = 512 + rng.randint(-18, 18)
    cy = 470 + rng.randint(-16, 24)
    if index in {2, 6, 10, 14, 21, 24, 26, 32}:
        face_w -= 70
        face_h += 80
    if index in {1, 7, 13, 19, 29}:
        face_w += 90
        face_h -= 10
    if index in {3, 16, 30}:
        face_w += 40
        face_h += 20

    skin = (236 + rng.randint(-8, 8), 190 + rng.randint(-8, 10), 150 + rng.randint(-6, 8), 224)
    line = (70, 48, 35, 210)
    box = (cx - face_w // 2, cy - face_h // 2, cx + face_w // 2, cy + face_h // 2)

    ear_y = cy - face_h // 12
    ear_size = 96 + (index % 4) * 10
    paint_ellipse(image, (box[0] - 56, ear_y - 52, box[0] + 42, ear_y + ear_size), skin, line, rng, 5)
    paint_ellipse(image, (box[2] - 42, ear_y - 52, box[2] + 56, ear_y + ear_size), skin, line, rng, 5)
    paint_ellipse(image, box, skin, line, rng, 6)

    if index not in {20}:
        hair = rng.choice([(55, 40, 32, 230), (43, 38, 32, 230), (76, 51, 39, 230), (38, 42, 35, 230)])
        hair_top = box[1] - 14
        if index in {19, 31}:
            for _ in range(15):
                hx = rng.randint(box[0] + 58, box[2] - 58)
                hy = rng.randint(hair_top, box[1] + 95)
                r = rng.randint(34, 62)
                draw.ellipse((hx - r, hy - r, hx + r, hy + r), fill=hair)
        else:
            draw.pieslice((box[0] + 18, hair_top, box[2] - 18, box[1] + 220), 180, 360, fill=hair)
            for _ in range(7):
                x = rng.randint(box[0] + 60, box[2] - 60)
                draw.line([(x, box[1] + 28), (x + rng.randint(-60, 60), box[1] + rng.randint(120, 190))], fill=hair, width=18)

    blush = (238, 112, 100, 56)
    draw.ellipse((cx - face_w // 3 - 58, cy + 20, cx - face_w // 3 + 72, cy + 104), fill=blush)
    draw.ellipse((cx + face_w // 3 - 72, cy + 20, cx + face_w // 3 + 58, cy + 104), fill=blush)

    eye_y = cy - 38 + rng.randint(-10, 10)
    eye_gap = 150 + (index % 4) * 14
    if index in {1, 12, 13, 21, 32}:
        paint_line(image, [(cx - eye_gap, eye_y), (cx - eye_gap + 46, eye_y - 16), (cx - eye_gap + 92, eye_y)], line, rng, 10)
        paint_line(image, [(cx + eye_gap - 92, eye_y), (cx + eye_gap - 46, eye_y - 16), (cx + eye_gap, eye_y)], line, rng, 10)
    else:
        for side in (-1, 1):
            ex = cx + side * eye_gap // 2
            ew = 44 + (index % 3) * 7
            eh = 52 + (index % 5) * 4
            draw.ellipse((ex - ew, eye_y - eh // 2, ex + ew, eye_y + eh // 2), fill=(54, 39, 30, 235))
            draw.ellipse((ex - ew // 4, eye_y - eh // 3, ex + ew // 5, eye_y - eh // 12), fill=(255, 255, 255, 190))

    brow_y = eye_y - 80
    paint_line(image, [(cx - eye_gap // 2 - 62, brow_y), (cx - eye_gap // 2 + 50, brow_y - rng.randint(8, 30))], line, rng, 8)
    paint_line(image, [(cx + eye_gap // 2 - 50, brow_y - rng.randint(8, 30)), (cx + eye_gap // 2 + 62, brow_y)], line, rng, 8)

    nose_h = 34 + (index % 7) * 8
    paint_line(image, [(cx + rng.randint(-12, 12), cy + 4), (cx + rng.randint(-8, 8), cy + nose_h)], (134, 83, 63, 140), rng, 5)
    mouth_y = cy + 122 + rng.randint(-10, 16)
    if index in {30, 32}:
        paint_line(image, [(cx - 62, mouth_y), (cx + 62, mouth_y)], (130, 66, 55, 180), rng, 5)
    elif index in {31, 18}:
        paint_line(image, [(cx - 68, mouth_y), (cx - 8, mouth_y + 28), (cx + 68, mouth_y - 8)], (130, 66, 55, 180), rng, 5)
    else:
        draw.arc((cx - 92, mouth_y - 42, cx + 92, mouth_y + 58), 16, 164, fill=(130, 66, 55, 190), width=6)

    return image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=80, threshold=2))


def draw_local_body(asset: Asset, index: int) -> Image.Image:
    rng = random.Random(asset.seed)
    image = Image.new("RGBA", BODY_SOURCE_SIZE, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    cx = 512
    shoulder = 260 + rng.randint(-40, 60)
    torso_w = 310 + rng.randint(-60, 90)
    torso_h = 470 + rng.randint(-70, 80)
    leg_len = 420 + rng.randint(-90, 120)
    arm_len = 390 + rng.randint(-90, 110)

    if index in {2, 6, 7}:
        torso_w -= 55
        torso_h += 90
        leg_len += 120
        arm_len += 80
    if index in {3, 10, 13}:
        shoulder += 85
        torso_w += 90
    if index in {1, 4, 5, 8, 14}:
        torso_w += 40
        torso_h -= 40
        leg_len -= 90
        arm_len -= 55
    if index == 11:
        shoulder -= 30
    if index == 15:
        leg_len -= 20

    skin = (232, 184, 143, 230)
    body_fill = (220, 197, 162, 220)
    shade = (151, 110, 82, 70)
    line = (70, 48, 35, 205)

    neck_top = 310 + rng.randint(-14, 18)
    draw.rounded_rectangle((cx - 58, neck_top, cx + 58, neck_top + 118), radius=40, fill=skin, outline=line, width=5)

    shoulder_y = neck_top + 98
    waist_y = shoulder_y + torso_h
    hip_w = max(150, torso_w - 70)
    torso = [
        (cx - shoulder, shoulder_y),
        (cx + shoulder, shoulder_y),
        (cx + hip_w // 2, waist_y),
        (cx - hip_w // 2, waist_y),
    ]
    layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
    ldraw = ImageDraw.Draw(layer)
    for _ in range(12):
        jittered = [(x + rng.randint(-8, 8), y + rng.randint(-8, 8)) for x, y in torso]
        ldraw.polygon(jittered, fill=(body_fill[0], body_fill[1], body_fill[2], 36))
    layer = layer.filter(ImageFilter.GaussianBlur(1.6))
    image.alpha_composite(layer)
    draw = ImageDraw.Draw(image)
    draw.line(torso + [torso[0]], fill=line, width=7, joint="curve")
    draw.ellipse((cx - torso_w // 3, shoulder_y + 160, cx + torso_w // 3, waist_y + 60), fill=shade)

    left_hand = (cx - shoulder - 76, shoulder_y + arm_len)
    right_hand = (cx + shoulder + 76, shoulder_y + arm_len + rng.randint(-20, 20))
    paint_line(image, [(cx - shoulder + 20, shoulder_y + 28), (cx - shoulder - 42, shoulder_y + arm_len // 2), left_hand], skin, rng, 42)
    paint_line(image, [(cx + shoulder - 20, shoulder_y + 28), (cx + shoulder + 42, shoulder_y + arm_len // 2), right_hand], skin, rng, 42)
    paint_ellipse(image, (left_hand[0] - 50, left_hand[1] - 32, left_hand[0] + 50, left_hand[1] + 42), skin, line, rng, 4)
    paint_ellipse(image, (right_hand[0] - 50, right_hand[1] - 32, right_hand[0] + 50, right_hand[1] + 42), skin, line, rng, 4)

    leg_w = 70 + rng.randint(-8, 20)
    foot_y = min(1460, waist_y + leg_len)
    left_hip = cx - hip_w // 4
    right_hip = cx + hip_w // 4
    left_foot = cx - 86 - (30 if index == 15 else 0)
    right_foot = cx + 86 + (30 if index == 15 else 0)
    paint_line(image, [(left_hip, waist_y), (left_foot - rng.randint(0, 35), waist_y + leg_len // 2), (left_foot, foot_y)], skin, rng, leg_w)
    paint_line(image, [(right_hip, waist_y), (right_foot + rng.randint(0, 35), waist_y + leg_len // 2), (right_foot, foot_y)], skin, rng, leg_w)
    paint_ellipse(image, (left_foot - 78, foot_y - 22, left_foot + 48, foot_y + 40), skin, line, rng, 4)
    paint_ellipse(image, (right_foot - 48, foot_y - 22, right_foot + 78, foot_y + 40), skin, line, rng, 4)

    return image.filter(ImageFilter.UnsharpMask(radius=1.1, percent=70, threshold=2))


def save_local_public(source: Image.Image, public_path: Path, size: tuple[int, int]) -> None:
    fitted = ImageOps.contain(source.convert("RGBA"), size, method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (255, 255, 255, 0))
    canvas.alpha_composite(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
    canvas.save(public_path, format="PNG", optimize=True)


def main() -> None:
    args = parse_args()
    selected = set(args.only or [])
    client = None if args.reprocess or args.local_fallback else InferenceClient(provider=args.provider, token=token_from_env(args.token_file), timeout=240)

    for group, assets, source_size, public_size in target_sets(args.kind):
        raw_dir = RAW_ROOT / group
        public_dir = PUBLIC_ROOT / group
        raw_dir.mkdir(parents=True, exist_ok=True)
        public_dir.mkdir(parents=True, exist_ok=True)

        for asset in assets:
            if selected and asset.file not in selected:
                continue

            raw_path = raw_dir / asset.file
            public_path = public_dir / asset.file
            if raw_path.exists() and public_path.exists() and not args.force:
                print(f"skip {group}/{asset.file}")
                continue

            if args.reprocess:
                if not raw_path.exists():
                    print(f"missing raw {group}/{asset.file}")
                    continue
                print(f"reprocess {group}/{asset.file}")
                image = Image.open(raw_path).convert("RGB")
            elif args.local_fallback:
                print(f"local {group}/{asset.file}")
                index = int(asset.file.split("-")[1].split(".")[0])
                image = draw_local_face(asset, index) if group == "faces" else draw_local_body(asset, index)
                image.save(raw_path, format="PNG")
                save_local_public(image, public_path, public_size)
                continue
            else:
                if client is None:
                    raise RuntimeError("Inference client was not initialized.")
                print(f"generate {group}/{asset.file}")
                image = generate_asset(client, asset, args.model, source_size, args.steps, args.seed_offset, group)
                image.convert("RGB").save(raw_path, format="PNG")
            save_public_copy(image, public_path, public_size, group)

    save_contact_sheet()
    save_icons()
    print("done")


if __name__ == "__main__":
    main()
