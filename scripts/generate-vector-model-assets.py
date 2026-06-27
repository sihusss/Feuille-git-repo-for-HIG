#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Literal

import svgwrite


ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "public" / "assets" / "model_parts"
CANVAS = (512, 682)
COUNT = 24

LINE = "#2f2925"
SOFT_LINE = "#74675d"
WHITE = "#fbf8ef"
SHADOW = "#ead9bd"

SKINS = [
    "#f0bf91",
    "#d98c59",
    "#a76443",
    "#f4d0ab",
    "#7d523a",
    "#e7a66f",
    "#c5794f",
    "#f6dfc4",
]
HAIRS = ["#2d231f", "#5a3828", "#8e4d2e", "#c47235", "#e0d7c6", "#1f343a", "#6d2726", "#15191d"]
EYES = ["#334e67", "#3f633f", "#654630", "#57406d", "#22262a", "#8a5d2a"]


@dataclass(frozen=True)
class Part:
    folder: str
    prefix: str


@dataclass(frozen=True)
class FaceSpec:
    label: str
    face: Literal["round", "long", "square", "heart", "wide", "sharp"]
    hair: Literal["crop", "bob", "curly", "bun", "long", "spike", "parted", "balding"]
    expression: Literal["stern", "sly", "kind", "worried", "smug", "tired", "wide", "calm"]
    brow: Literal["heavy", "thin", "arched", "flat", "droop", "split"]
    skin: int
    hair_color: int
    eye: int
    complexion: Literal["clear", "acne", "cheek_acne", "forehead_acne", "freckles", "pimple_patch", "mole", "under_eye", "braces"]


@dataclass(frozen=True)
class ArmSpec:
    label: str
    pose: Literal[
        "down",
        "open",
        "crossed",
        "akimbo",
        "wave",
        "point",
        "clasp",
        "fold",
        "shrug",
        "pockets",
        "explain",
        "guard",
    ]
    sleeve: Literal["short", "rolled", "long", "wide", "bare"]
    build: Literal["thin", "average", "heavy"]
    skin: int
    cloth: str


@dataclass(frozen=True)
class TorsoSpec:
    label: str
    style: Literal[
        "tee",
        "vest",
        "blazer",
        "hoodie",
        "work",
        "coat",
        "apron",
        "dress",
        "sweater",
        "utility",
        "crop",
        "tunic",
    ]
    build: Literal["thin", "average", "stocky", "broad", "soft", "tall"]
    primary: str
    secondary: str


@dataclass(frozen=True)
class LegSpec:
    label: str
    style: Literal["straight", "wide", "shorts", "skirt", "cargo", "jogger", "bootcut", "longskirt"]
    height: Literal["short", "average", "tall"]
    build: Literal["thin", "average", "strong", "soft"]
    primary: str
    secondary: str
    skin: int


PARTS = {
    "head": Part("heads", "head_"),
    "arms": Part("arms", "arms_"),
    "torso": Part("torsos", "torso_"),
    "legs": Part("legs", "legs_"),
}

FACES: list[FaceSpec] = [
    FaceSpec("이마 여드름과 짙은 눈썹 얼굴", "square", "crop", "stern", "heavy", 0, 0, 4, "forehead_acne"),
    FaceSpec("볼 여드름과 얇은 입술 얼굴", "sharp", "parted", "sly", "thin", 1, 5, 2, "cheek_acne"),
    FaceSpec("여드름 패치를 붙인 큰 눈 얼굴", "round", "bob", "wide", "arched", 3, 3, 0, "pimple_patch"),
    FaceSpec("피곤한 다크서클 걱정 얼굴", "long", "long", "worried", "droop", 5, 1, 1, "under_eye"),
    FaceSpec("주근깨가 있는 온화한 얼굴", "heart", "curly", "kind", "arched", 7, 4, 3, "freckles"),
    FaceSpec("넓은 볼과 자신만만한 얼굴", "wide", "spike", "smug", "split", 2, 0, 5, "clear"),
    FaceSpec("턱 여드름과 피곤한 눈매 얼굴", "long", "balding", "tired", "flat", 4, 7, 4, "acne"),
    FaceSpec("점이 있는 차분한 얼굴", "square", "bob", "calm", "flat", 6, 2, 1, "mole"),
    FaceSpec("여드름 흉터 느낌의 엄격한 얼굴", "sharp", "crop", "stern", "heavy", 4, 5, 0, "acne"),
    FaceSpec("주근깨와 둥근 볼 웃는 얼굴", "round", "curly", "kind", "arched", 0, 6, 1, "freckles"),
    FaceSpec("볼 여드름과 의심스러운 눈매", "heart", "long", "sly", "thin", 1, 0, 4, "cheek_acne"),
    FaceSpec("치아 교정기가 보이는 놀란 얼굴", "wide", "parted", "wide", "arched", 3, 1, 3, "braces"),
    FaceSpec("두꺼운 눈썹과 이마 여드름 얼굴", "square", "spike", "stern", "heavy", 5, 7, 5, "forehead_acne"),
    FaceSpec("작은 입과 깨끗한 피부 얼굴", "long", "bob", "calm", "flat", 7, 4, 2, "clear"),
    FaceSpec("여드름 패치와 소심한 얼굴", "heart", "crop", "worried", "droop", 2, 0, 1, "pimple_patch"),
    FaceSpec("한쪽 입꼬리와 볼 점 얼굴", "sharp", "curly", "smug", "split", 6, 3, 0, "mole"),
    FaceSpec("긴 코와 다크서클 냉정 얼굴", "long", "parted", "stern", "thin", 0, 1, 4, "under_eye"),
    FaceSpec("넓은 얼굴과 볼 여드름 인상", "wide", "bob", "kind", "arched", 4, 2, 1, "cheek_acne"),
    FaceSpec("짧은 앞머리와 턱 여드름 얼굴", "square", "crop", "sly", "heavy", 3, 7, 5, "acne"),
    FaceSpec("반쯤 감긴 눈과 다크서클 얼굴", "round", "long", "tired", "droop", 5, 5, 3, "under_eye"),
    FaceSpec("작고 예민한 여드름 패치 얼굴", "sharp", "spike", "worried", "thin", 7, 6, 0, "pimple_patch"),
    FaceSpec("넓은 미소와 교정기 얼굴", "round", "curly", "kind", "arched", 1, 3, 1, "braces"),
    FaceSpec("직선 눈썹과 주근깨 얼굴", "heart", "balding", "calm", "flat", 2, 0, 4, "freckles"),
    FaceSpec("활달한 눈과 이마 여드름 얼굴", "wide", "parted", "wide", "split", 6, 2, 5, "forehead_acne"),
]

ARMS: list[ArmSpec] = [
    ArmSpec("축 늘어진 긴소매 팔", "down", "long", "thin", 0, "#415063"),
    ArmSpec("넓게 벌린 환영 팔", "open", "rolled", "average", 1, "#c46d3d"),
    ArmSpec("가슴 앞에 교차한 팔", "crossed", "long", "average", 2, "#2f343a"),
    ArmSpec("허리에 얹은 당당한 팔", "akimbo", "short", "heavy", 3, "#e2c46d"),
    ArmSpec("한손 높이 흔드는 팔", "wave", "rolled", "thin", 4, "#6f8f58"),
    ArmSpec("삿대질하는 날카로운 팔", "point", "long", "average", 5, "#9d3c34"),
    ArmSpec("앞에서 손을 모은 팔", "clasp", "wide", "thin", 6, "#efe5d0"),
    ArmSpec("팔짱 낀 방어적 팔", "fold", "long", "heavy", 7, "#3d3f45"),
    ArmSpec("어깨를 으쓱한 팔", "shrug", "short", "average", 0, "#b8d0df"),
    ArmSpec("주머니에 찔러 넣은 팔", "pockets", "long", "average", 1, "#2d5f72"),
    ArmSpec("설명하듯 벌린 팔", "explain", "rolled", "thin", 2, "#caa157"),
    ArmSpec("몸을 가리는 경계 팔", "guard", "wide", "average", 3, "#6c4d3b"),
    ArmSpec("무겁게 내린 두꺼운 팔", "down", "long", "heavy", 4, "#5a5c62"),
    ArmSpec("짧은소매 활짝 편 팔", "open", "short", "thin", 5, "#f2f0e8"),
    ArmSpec("단정히 모은 긴 팔", "clasp", "long", "average", 6, "#33528a"),
    ArmSpec("한쪽만 허리에 둔 팔", "akimbo", "rolled", "average", 7, "#8b613e"),
    ArmSpec("소매 큰 손짓 팔", "wave", "wide", "thin", 0, "#d7c4a2"),
    ArmSpec("앞을 찌르는 설명 팔", "point", "rolled", "heavy", 1, "#263946"),
    ArmSpec("맨팔로 벌린 팔", "open", "bare", "average", 2, "#f5efe4"),
    ArmSpec("작게 접은 경계 팔", "guard", "long", "thin", 3, "#7e8790"),
    ArmSpec("느슨한 팔짱 팔", "fold", "rolled", "average", 4, "#be5c3a"),
    ArmSpec("양손 주머니 팔", "pockets", "wide", "heavy", 5, "#20242a"),
    ArmSpec("차분히 내린 반소매 팔", "down", "short", "average", 6, "#6b7b48"),
    ArmSpec("크게 설명하는 팔", "explain", "wide", "heavy", 7, "#d99042"),
]

TORSOS: list[TorsoSpec] = [
    TorsoSpec("마른 흉곽이 보이는 티셔츠", "tee", "thin", "#f4f1e8", "#44586b"),
    TorsoSpec("살집 있는 둥근 배 니트 조끼", "vest", "soft", "#c9a24b", "#f7efd8"),
    TorsoSpec("넓은 어깨와 큰 상체 블레이저", "blazer", "broad", "#30343a", "#f5f2e8"),
    TorsoSpec("평균 체형 짧은 후디", "hoodie", "average", "#59718a", "#eef3f2"),
    TorsoSpec("탄탄하고 두꺼운 몸통 작업복", "work", "stocky", "#8a6a42", "#e8d6b2"),
    TorsoSpec("키 큰 긴 코트 몸통", "coat", "tall", "#5d5f63", "#282a2d"),
    TorsoSpec("평균 체형 앞치마 몸통", "apron", "average", "#e9e2d3", "#3e665b"),
    TorsoSpec("살집 있는 넓은 원피스 몸통", "dress", "soft", "#9d4553", "#f6e7d2"),
    TorsoSpec("두꺼운 상체 줄무늬 스웨터", "sweater", "stocky", "#345d5b", "#eadfbd"),
    TorsoSpec("넓은 어깨 유틸리티 조끼", "utility", "broad", "#6f774d", "#f5edd6"),
    TorsoSpec("마른 허리 짧은 크롭 재킷", "crop", "thin", "#bf6b3d", "#f9f1e6"),
    TorsoSpec("키 큰 긴 튜닉 셔츠", "tunic", "tall", "#d9d1bd", "#4a3d34"),
    TorsoSpec("마른 목폴라 몸통", "tee", "thin", "#3f4248", "#ebe5da"),
    TorsoSpec("살집 있는 풍성한 가디건", "vest", "soft", "#d6b177", "#fff7e6"),
    TorsoSpec("넓은 어깨 각진 제복 재킷", "blazer", "broad", "#263e5c", "#f4f0e5"),
    TorsoSpec("두꺼운 체형 헐렁한 후드", "hoodie", "stocky", "#768184", "#f7f7ef"),
    TorsoSpec("평균 체형 페인트 작업복", "work", "average", "#58684b", "#f1dfbe"),
    TorsoSpec("마른 몸을 덮는 긴 외투", "coat", "thin", "#6f5948", "#eee7d8"),
    TorsoSpec("살집 있는 요리사 앞치마", "apron", "soft", "#f5f3e9", "#b64535"),
    TorsoSpec("키 큰 주름 드레스 몸통", "dress", "tall", "#4d6588", "#f7e9d2"),
    TorsoSpec("둥근 배가 보이는 스웨터", "sweater", "soft", "#bc4e37", "#f3e7cf"),
    TorsoSpec("평균 체형 탐험가 조끼", "utility", "average", "#b58f48", "#f8efd8"),
    TorsoSpec("넓은 어깨 짧은 재킷", "crop", "broad", "#22272d", "#d4dae0"),
    TorsoSpec("두꺼운 체형 넉넉한 긴 셔츠", "tunic", "stocky", "#78a0b7", "#f5f1e7"),
]

LEGS: list[LegSpec] = [
    LegSpec("작은 키 마른 일자 바지", "straight", "short", "thin", "#2b3039", "#f5f2e8", 0),
    LegSpec("큰 키 평균 와이드 팬츠", "wide", "tall", "average", "#4a78a7", "#f9f8f1", 1),
    LegSpec("평균 키 튼튼한 반바지 하체", "shorts", "average", "strong", "#7faad0", "#22252a", 2),
    LegSpec("작은 키 둥근 긴 치마", "longskirt", "short", "soft", "#6a4d75", "#f6eee1", 3),
    LegSpec("평균 키 탄탄한 카고 바지", "cargo", "average", "strong", "#8b7a56", "#2f332e", 4),
    LegSpec("작은 키 살집 있는 조거", "jogger", "short", "soft", "#babec4", "#f4f1e8", 5),
    LegSpec("큰 키 마른 부츠컷", "bootcut", "tall", "thin", "#26344f", "#f5f2eb", 6),
    LegSpec("평균 키 보통 체형 짧은 치마", "skirt", "average", "average", "#bf3740", "#222329", 7),
    LegSpec("평균 키 살집 있는 넓은 바지", "wide", "average", "soft", "#202226", "#f4f4ee", 0),
    LegSpec("작은 키 마른 데님 반바지", "shorts", "short", "thin", "#5a9bc9", "#fbf8f0", 1),
    LegSpec("평균 키 단단한 직선 바지", "straight", "average", "strong", "#3c5b42", "#493328", 2),
    LegSpec("큰 키 마른 긴 치마", "longskirt", "tall", "thin", "#314a6b", "#f8f4e8", 3),
    LegSpec("작은 키 둥근 카고 하체", "cargo", "short", "soft", "#e7d8b6", "#5d402e", 4),
    LegSpec("큰 키 마른 조거 하체", "jogger", "tall", "thin", "#2a2c32", "#f3f1e8", 5),
    LegSpec("평균 키 튼튼한 부츠컷", "bootcut", "average", "strong", "#665f67", "#ede8db", 6),
    LegSpec("작은 키 보통 플리츠 치마", "skirt", "short", "average", "#315f72", "#f7f0df", 7),
    LegSpec("큰 키 평균 일자 바지", "straight", "tall", "average", "#e7e2d1", "#2d2925", 0),
    LegSpec("작은 키 튼튼한 와이드 데님", "wide", "short", "strong", "#315f8b", "#f9f8f1", 1),
    LegSpec("평균 키 살집 있는 운동 반바지", "shorts", "average", "soft", "#2b2c31", "#f5f2e8", 2),
    LegSpec("평균 키 둥근 긴 치마", "longskirt", "average", "soft", "#24242a", "#ece7da", 3),
    LegSpec("큰 키 평균 카고 바지", "cargo", "tall", "average", "#6f7953", "#efe5ce", 4),
    LegSpec("작은 키 보통 회색 조거", "jogger", "short", "average", "#9aa0a8", "#f8f5ed", 5),
    LegSpec("큰 키 아주 마른 부츠컷", "bootcut", "tall", "thin", "#181b20", "#f4f1e8", 6),
    LegSpec("평균 키 튼튼한 체크 치마", "skirt", "average", "strong", "#b64639", "#272322", 7),
]


def drawing(path: Path) -> svgwrite.Drawing:
    return svgwrite.Drawing(str(path), size=CANVAS, viewBox=f"0 0 {CANVAS[0]} {CANVAS[1]}", profile="full")


def attrs(fill: str, stroke: str = LINE, width: float = 3, **extra):
    return {
        "fill": fill,
        "stroke": stroke,
        "stroke_width": width,
        "stroke_linejoin": "round",
        "stroke_linecap": "round",
        **extra,
    }


def darker(hex_color: str, amount: int = 24) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"#{max(0, r - amount):02x}{max(0, g - amount):02x}{max(0, b - amount):02x}"


def lighter(hex_color: str, amount: int = 24) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"#{min(255, r + amount):02x}{min(255, g + amount):02x}{min(255, b + amount):02x}"


def line(dwg: svgwrite.Drawing, start, end, color=LINE, width=3):
    dwg.add(dwg.line(start=start, end=end, stroke=color, stroke_width=width, stroke_linecap="round"))


def path(dwg: svgwrite.Drawing, data: str, stroke=LINE, width=3, fill="none"):
    dwg.add(dwg.path(d=data, fill=fill, stroke=stroke, stroke_width=width, stroke_linecap="round", stroke_linejoin="round"))


def face_dims(face: str, rng: Random) -> tuple[int, int, int]:
    table = {
        "round": (114, 126, 24),
        "long": (96, 146, 18),
        "square": (112, 128, 12),
        "heart": (108, 134, 28),
        "wide": (126, 120, 20),
        "sharp": (98, 136, 10),
    }
    w, h, jaw = table[face]
    return w + rng.randint(-3, 3), h + rng.randint(-3, 4), jaw


def draw_hair(dwg: svgwrite.Drawing, spec: FaceSpec, cx: int, top: int, face_w: int, face_h: int):
    hair = HAIRS[spec.hair_color]
    if spec.hair == "crop":
        dwg.add(dwg.path(d=f"M {cx-face_w/2-15} {top+35} Q {cx} {top-30} {cx+face_w/2+18} {top+35} L {cx+face_w/2+6} {top+76} Q {cx} {top+40} {cx-face_w/2-8} {top+76} Z", **attrs(hair, LINE, 3)))
    elif spec.hair == "bob":
        dwg.add(dwg.rect(insert=(cx - face_w / 2 - 17, top - 12), size=(face_w + 34, face_h * 0.78), rx=34, **attrs(hair, LINE, 3)))
        dwg.add(dwg.rect(insert=(cx - face_w / 2 - 8, top + 48), size=(face_w + 16, 40), rx=8, fill=hair, stroke=hair, stroke_width=1))
    elif spec.hair == "curly":
        for n in range(11):
            x = cx - 62 + n * 12
            y = top + 7 + abs(n - 5) * 4
            dwg.add(dwg.ellipse(center=(x, y), r=(21, 20), **attrs(hair, LINE, 2)))
        for side in (-1, 1):
            for n in range(4):
                dwg.add(dwg.circle(center=(cx + side * (face_w / 2 + 8 + n * 4), top + 48 + n * 23), r=15, **attrs(hair, LINE, 2)))
    elif spec.hair == "bun":
        dwg.add(dwg.ellipse(center=(cx, top + 17), r=(face_w / 2 + 14, 46), **attrs(hair, LINE, 3)))
        dwg.add(dwg.circle(center=(cx + 4, top - 29), r=27, **attrs(hair, LINE, 3)))
    elif spec.hair == "long":
        dwg.add(dwg.ellipse(center=(cx, top + 18), r=(face_w / 2 + 20, 50), **attrs(hair, LINE, 3)))
        for side in (-1, 1):
            dwg.add(dwg.path(d=f"M {cx+side*48} {top+35} C {cx+side*80} {top+88}, {cx+side*74} {top+150}, {cx+side*46} {top+178}", fill="none", stroke=hair, stroke_width=20, stroke_linecap="round"))
    elif spec.hair == "spike":
        dwg.add(dwg.path(d=f"M {cx-face_w/2-14} {top+40} L {cx-42} {top-3} L {cx-18} {top+12} L {cx-2} {top-28} L {cx+17} {top+14} L {cx+45} {top-2} L {cx+face_w/2+15} {top+42} Q {cx} {top+24} {cx-face_w/2-14} {top+40} Z", **attrs(hair, LINE, 3)))
    elif spec.hair == "parted":
        dwg.add(dwg.ellipse(center=(cx, top + 19), r=(face_w / 2 + 16, 47), **attrs(hair, LINE, 3)))
        path(dwg, f"M {cx+5} {top-17} Q {cx-2} {top+24} {cx-44} {top+65}", stroke=darker(hair, 36), width=3)
    elif spec.hair == "balding":
        dwg.add(dwg.path(d=f"M {cx-face_w/2-4} {top+54} Q {cx} {top-16} {cx+face_w/2+4} {top+54} Q {cx+20} {top+35} {cx} {top+36} Q {cx-20} {top+35} {cx-face_w/2-4} {top+54} Z", **attrs(hair, LINE, 3)))


def draw_brows_and_eyes(dwg: svgwrite.Drawing, spec: FaceSpec, cx: int, eye_y: int, eye_color: str):
    eye_shapes = {
        "stern": (15, 7),
        "sly": (16, 5),
        "kind": (16, 9),
        "worried": (14, 8),
        "smug": (15, 6),
        "tired": (16, 4),
        "wide": (18, 12),
        "calm": (14, 6),
    }
    ew, eh = eye_shapes[spec.expression]
    for side in (-1, 1):
        ex = cx + side * 29
        if spec.expression == "tired":
            path(dwg, f"M {ex-ew} {eye_y} Q {ex} {eye_y+eh} {ex+ew} {eye_y}", width=2.4)
        else:
            dwg.add(dwg.ellipse(center=(ex, eye_y), r=(ew, eh), **attrs(WHITE, LINE, 2.2)))
            dwg.add(dwg.circle(center=(ex + side * 2, eye_y + 1), r=4.8, fill=eye_color, stroke=LINE, stroke_width=1.2))

        if spec.brow == "heavy":
            line(dwg, (ex - side * 20, eye_y - 22), (ex + side * 19, eye_y - 15), LINE, 6)
        elif spec.brow == "thin":
            line(dwg, (ex - side * 18, eye_y - 18), (ex + side * 17, eye_y - 20), LINE, 2)
        elif spec.brow == "arched":
            path(dwg, f"M {ex-side*18} {eye_y-18} Q {ex} {eye_y-28} {ex+side*18} {eye_y-18}", width=3)
        elif spec.brow == "droop":
            line(dwg, (ex - side * 18, eye_y - 19), (ex + side * 18, eye_y - 13), LINE, 3.5)
        elif spec.brow == "split":
            line(dwg, (ex - side * 19, eye_y - 22), (ex + side * 1, eye_y - 18), LINE, 3.4)
            line(dwg, (ex + side * 7, eye_y - 17), (ex + side * 20, eye_y - 14), LINE, 3.4)
        else:
            line(dwg, (ex - 18, eye_y - 17), (ex + 18, eye_y - 17), LINE, 3)


def draw_mouth(dwg: svgwrite.Drawing, expression: str, cx: int, y: int):
    if expression == "stern":
        line(dwg, (cx - 18, y), (cx + 17, y - 1), "#713d38", 3)
    elif expression == "sly":
        path(dwg, f"M {cx-17} {y+2} Q {cx+2} {y+11} {cx+24} {y-3}", stroke="#713d38", width=3)
    elif expression == "kind":
        path(dwg, f"M {cx-22} {y-3} Q {cx} {y+18} {cx+23} {y-3}", stroke="#8a443d", width=3)
    elif expression == "worried":
        path(dwg, f"M {cx-18} {y+8} Q {cx} {y-5} {cx+18} {y+8}", stroke="#713d38", width=3)
    elif expression == "smug":
        path(dwg, f"M {cx-19} {y+2} Q {cx+2} {y+4} {cx+21} {y-7}", stroke="#713d38", width=3)
    elif expression == "tired":
        line(dwg, (cx - 15, y + 1), (cx + 15, y + 1), "#713d38", 2)
    elif expression == "wide":
        dwg.add(dwg.ellipse(center=(cx, y + 3), r=(12, 16), fill="#6c3734", stroke=LINE, stroke_width=2))
    else:
        path(dwg, f"M {cx-15} {y} Q {cx} {y+5} {cx+15} {y}", stroke="#713d38", width=2.6)


def draw_complexion(dwg: svgwrite.Drawing, complexion: str, cx: int, top: int, face_w: int, face_h: int):
    acne = "#b95a58"
    freckle = "#9b6543"
    patch = "#dfeee9"
    if complexion == "clear":
        return
    if complexion == "acne":
        marks = [(-22, 104, 4), (-9, 114, 3), (19, 108, 3.5), (7, 126, 3), (29, 121, 2.6)]
        for dx, dy, radius in marks:
            dwg.add(dwg.circle(center=(cx + dx, top + dy), r=radius, fill=acne, opacity=0.82))
    elif complexion == "cheek_acne":
        for side in (-1, 1):
            for n, (dx, dy) in enumerate([(33, 94), (41, 108), (26, 116)]):
                dwg.add(dwg.circle(center=(cx + side * dx, top + dy + n), r=3.2, fill=acne, opacity=0.8))
    elif complexion == "forehead_acne":
        for dx, dy, radius in [(-24, 53, 3.2), (-9, 47, 2.7), (11, 51, 3.4), (27, 58, 2.5)]:
            dwg.add(dwg.circle(center=(cx + dx, top + dy), r=radius, fill=acne, opacity=0.82))
    elif complexion == "freckles":
        for side in (-1, 1):
            for n in range(5):
                dwg.add(dwg.circle(center=(cx + side * (18 + n * 6), top + 101 + (n % 2) * 5), r=1.9, fill=freckle, opacity=0.75))
    elif complexion == "pimple_patch":
        for dx, dy in [(-30, 104), (24, 94)]:
            dwg.add(dwg.rect(insert=(cx + dx - 7, top + dy - 6), size=(14, 12), rx=4, fill=patch, stroke=SOFT_LINE, stroke_width=1.5))
            line(dwg, (cx + dx - 4, top + dy), (cx + dx + 4, top + dy), SOFT_LINE, 1.4)
            line(dwg, (cx + dx, top + dy - 4), (cx + dx, top + dy + 4), SOFT_LINE, 1.4)
    elif complexion == "mole":
        dwg.add(dwg.circle(center=(cx + face_w * 0.25, top + 112), r=3.2, fill="#4d342c", stroke=LINE, stroke_width=0.8))
    elif complexion == "under_eye":
        for side in (-1, 1):
            path(dwg, f"M {cx+side*15} {top+95} Q {cx+side*29} {top+103} {cx+side*43} {top+96}", stroke="#8b756a", width=2)
    elif complexion == "braces":
        mouth_y = top + face_h + 1
        line(dwg, (cx - 18, mouth_y), (cx + 18, mouth_y), "#d9e1e3", 2.2)
        for dx in (-12, -4, 4, 12):
            dwg.add(dwg.rect(insert=(cx + dx - 2.2, mouth_y - 2.6), size=(4.4, 5.2), rx=1, fill=WHITE, stroke=SOFT_LINE, stroke_width=0.8))


def draw_head(path_out: Path, index: int):
    rng = Random(11000 + index)
    spec = FACES[index]
    dwg = drawing(path_out)
    skin = SKINS[spec.skin]
    eye_color = EYES[spec.eye]
    cx = 256 + rng.randint(-3, 3)
    top = 70 + rng.randint(-2, 4)
    face_w, face_h, jaw = face_dims(spec.face, rng)

    neck_w = 38 if spec.face != "wide" else 46
    dwg.add(dwg.rect(insert=(cx - neck_w / 2, top + face_h - 3), size=(neck_w, 58), rx=12, **attrs(darker(skin, 8), SOFT_LINE, 2)))
    draw_hair(dwg, spec, cx, top, face_w, face_h)

    if spec.face in ("sharp", "heart"):
        points = [
            (cx - face_w / 2, top + 42),
            (cx - face_w / 2 + 8, top + face_h - 24),
            (cx, top + face_h + jaw / 2),
            (cx + face_w / 2 - 8, top + face_h - 24),
            (cx + face_w / 2, top + 42),
        ]
        dwg.add(dwg.polygon(points=points, **attrs(skin, LINE, 3)))
    elif spec.face == "square":
        dwg.add(dwg.rect(insert=(cx - face_w / 2, top + 20), size=(face_w, face_h), rx=18, **attrs(skin, LINE, 3)))
    else:
        dwg.add(dwg.ellipse(center=(cx, top + face_h / 2 + 16), r=(face_w / 2, face_h / 2), **attrs(skin, LINE, 3)))

    for side in (-1, 1):
        dwg.add(dwg.ellipse(center=(cx + side * (face_w / 2 + 4), top + 78), r=(10, 15), **attrs(skin, SOFT_LINE, 2)))

    draw_brows_and_eyes(dwg, spec, cx, top + 82, eye_color)
    nose_len = 19 if spec.face == "long" else 14
    path(dwg, f"M {cx+2} {top+94} L {cx-5} {top+94+nose_len} L {cx+6} {top+95+nose_len}", stroke=darker(skin, 44), width=2)
    draw_mouth(dwg, spec.expression, cx, top + face_h - 2)
    draw_complexion(dwg, spec.complexion, cx, top, face_w, face_h)

    if index % 4 == 0:
        for side in (-1, 1):
            dwg.add(dwg.circle(center=(cx + side * (face_w / 2 + 12), top + 110), r=5, fill="#c99a42", stroke=LINE, stroke_width=1.5))
    if index in {1, 6, 12, 18}:
        dwg.add(dwg.rect(insert=(cx - 45, top + 72), size=(90, 22), rx=10, fill="none", stroke=LINE, stroke_width=3))
        line(dwg, (cx - 8, top + 83), (cx + 8, top + 83), LINE, 2)
    dwg.save()


def pose_points(pose: str) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    poses = {
        "down": ([(175, 232), (155, 314), (142, 414)], [(337, 232), (357, 314), (370, 414)]),
        "open": ([(175, 238), (125, 296), (84, 350)], [(337, 238), (387, 296), (428, 350)]),
        "crossed": ([(171, 244), (214, 312), (300, 350)], [(341, 244), (300, 312), (210, 350)]),
        "akimbo": ([(174, 240), (130, 302), (162, 374)], [(338, 240), (382, 302), (350, 374)]),
        "wave": ([(176, 238), (146, 320), (140, 414)], [(336, 238), (392, 174), (428, 108)]),
        "point": ([(175, 238), (145, 314), (132, 410)], [(337, 239), (393, 298), (456, 304)]),
        "clasp": ([(174, 236), (210, 308), (252, 370)], [(338, 236), (302, 308), (260, 370)]),
        "fold": ([(174, 240), (222, 298), (311, 324)], [(338, 240), (290, 300), (203, 330)]),
        "shrug": ([(174, 232), (121, 244), (98, 296)], [(338, 232), (391, 244), (414, 296)]),
        "pockets": ([(176, 236), (170, 314), (205, 400)], [(336, 236), (342, 314), (307, 400)]),
        "explain": ([(174, 238), (126, 288), (93, 326)], [(338, 238), (386, 288), (419, 326)]),
        "guard": ([(174, 240), (219, 304), (275, 358)], [(338, 240), (300, 318), (240, 376)]),
    }
    return poses[pose]


def add_limb_segment(
    dwg: svgwrite.Drawing,
    pts: list[tuple[float, float]],
    color: str,
    width: float,
    start: int,
    end: int,
):
    segment = pts[start : end + 1]
    dwg.add(dwg.polyline(points=segment, fill="none", stroke=darker(color, 34), stroke_width=width + 8, stroke_linecap="round", stroke_linejoin="round"))
    dwg.add(dwg.polyline(points=segment, fill="none", stroke=color, stroke_width=width, stroke_linecap="round", stroke_linejoin="round"))


def draw_hand(dwg: svgwrite.Drawing, x: float, y: float, skin: str, direction: int, big: bool):
    scale = 1.15 if big else 1
    dwg.add(dwg.ellipse(center=(x, y), r=(12 * scale, 15 * scale), **attrs(skin, LINE, 2)))
    for n in range(4):
        dx = direction * (n - 1.4) * 4.3 * scale
        line(dwg, (x + dx, y + 9 * scale), (x + dx + direction * (n - 1.4) * 1.8, y + 22 * scale), darker(skin, 12), 2.6 * scale)


def draw_arms(path_out: Path, index: int):
    spec = ARMS[index]
    dwg = drawing(path_out)
    skin = SKINS[spec.skin]
    cloth = spec.cloth
    width = {"thin": 18, "average": 23, "heavy": 29}[spec.build]
    left, right = pose_points(spec.pose)

    for side, pts in [(-1, left), (1, right)]:
        cuff_index = 1 if spec.sleeve == "short" else 2
        if spec.sleeve == "bare":
            add_limb_segment(dwg, pts, skin, max(15, width - 4), 0, 2)
        elif spec.sleeve == "short":
            add_limb_segment(dwg, pts, cloth, width + 4, 0, 1)
            add_limb_segment(dwg, pts, skin, max(14, width - 7), 1, 2)
        elif spec.sleeve == "rolled":
            add_limb_segment(dwg, pts, cloth, width + 4, 0, 1)
            add_limb_segment(dwg, pts, skin, max(14, width - 6), 1, 2)
            dwg.add(dwg.circle(center=pts[1], r=width / 2 + 4, fill=lighter(cloth, 18), stroke=LINE, stroke_width=2))
        elif spec.sleeve == "wide":
            add_limb_segment(dwg, pts, cloth, width + 12, 0, 2)
        else:
            add_limb_segment(dwg, pts, cloth, width + 4, 0, 2)

        hx, hy = pts[-1]
        if spec.pose == "point" and side == 1:
            line(dwg, (hx - 3, hy - 2), (hx + 42, hy - 2), skin, 6)
            line(dwg, (hx - 3, hy - 2), (hx + 42, hy - 2), LINE, 2)
        elif spec.pose == "wave" and side == 1:
            draw_hand(dwg, hx, hy, skin, side, spec.build == "heavy")
            for dy in (-32, -18, -4):
                path(dwg, f"M {hx+18} {hy+dy} Q {hx+37} {hy+dy-12} {hx+56} {hy+dy}", stroke=SOFT_LINE, width=2)
        else:
            draw_hand(dwg, hx, hy, skin, side, spec.build == "heavy")

        if spec.sleeve != "bare" and cuff_index < len(pts):
            cx, cy = pts[cuff_index]
            dwg.add(dwg.circle(center=(cx, cy), r=width / 2 + 3, fill=lighter(cloth, 12), stroke=LINE, stroke_width=2))

    dwg.save()


def body_dims(build: str) -> tuple[int, int, int, int]:
    return {
        "thin": (138, 88, 214, 420),
        "average": (174, 126, 212, 430),
        "stocky": (206, 174, 214, 442),
        "broad": (226, 136, 210, 430),
        "soft": (196, 188, 216, 448),
        "tall": (162, 108, 190, 456),
    }[build]


def draw_torso_base(dwg: svgwrite.Drawing, spec: TorsoSpec):
    cx = 256
    shoulder, waist, top, bottom = body_dims(spec.build)
    primary, secondary = spec.primary, spec.secondary
    body = [
        (cx - shoulder / 2, top + 24),
        (cx + shoulder / 2, top + 24),
        (cx + waist / 2, bottom),
        (cx - waist / 2, bottom),
    ]
    dwg.add(dwg.polygon(points=body, **attrs(primary, LINE, 4)))
    if spec.build == "thin":
        for y in (top + 116, top + 145):
            path(dwg, f"M {cx-42} {y} Q {cx-20} {y-10} {cx-7} {y}", stroke=lighter(primary, 46), width=2)
            path(dwg, f"M {cx+42} {y} Q {cx+20} {y-10} {cx+7} {y}", stroke=lighter(primary, 46), width=2)
        path(dwg, f"M {cx-48} {bottom-46} Q {cx} {bottom-20} {cx+48} {bottom-46}", stroke=darker(primary, 34), width=2)
    elif spec.build in {"soft", "stocky"}:
        belly_y = bottom - 72 if spec.build == "soft" else bottom - 82
        path(dwg, f"M {cx-waist/2+18} {belly_y} Q {cx} {belly_y+36} {cx+waist/2-18} {belly_y}", stroke=lighter(primary, 38), width=4)
        path(dwg, f"M {cx-waist/2+8} {bottom-36} Q {cx} {bottom-7} {cx+waist/2-8} {bottom-36}", stroke=darker(primary, 28), width=2)
    elif spec.build == "broad":
        line(dwg, (cx - shoulder / 2 + 16, top + 62), (cx + shoulder / 2 - 16, top + 62), lighter(primary, 42), 4)
        line(dwg, (cx - shoulder / 2 + 28, top + 86), (cx + shoulder / 2 - 28, top + 86), lighter(primary, 32), 3)
    for side in (-1, 1):
        dwg.add(dwg.ellipse(center=(cx + side * (shoulder / 2 - 5), top + 42), r=(24, 28), fill=primary, stroke=LINE, stroke_width=3))
    dwg.add(dwg.polygon(points=[(cx - 42, top + 5), (cx + 42, top + 5), (cx + 30, top + 50), (cx - 30, top + 50)], **attrs(secondary, LINE, 2)))
    return cx, shoulder, waist, top, bottom


def draw_torso(path_out: Path, index: int):
    spec = TORSOS[index]
    dwg = drawing(path_out)
    cx, shoulder, waist, top, bottom = draw_torso_base(dwg, spec)
    primary, secondary = spec.primary, spec.secondary

    if spec.style in {"blazer", "coat"}:
        for side in (-1, 1):
            dwg.add(dwg.polygon(points=[(cx + side * 6, top + 40), (cx + side * (shoulder / 2 - 12), top + 34), (cx + side * (waist / 2 - 14), bottom - 6), (cx + side * 18, bottom - 6)], **attrs(darker(primary, 18), LINE, 2.5)))
        path(dwg, f"M {cx-46} {top+22} L {cx} {top+88} L {cx+46} {top+22}", stroke=SOFT_LINE, width=2, fill=secondary)
    elif spec.style == "hoodie":
        path(dwg, f"M {cx-48} {top+28} Q {cx} {top-8} {cx+48} {top+28}", stroke=secondary, width=11)
        dwg.add(dwg.rect(insert=(cx - 42, bottom - 72), size=(84, 46), rx=12, fill=darker(primary, 18), stroke=LINE, stroke_width=2))
    elif spec.style == "work":
        for side in (-1, 1):
            dwg.add(dwg.rect(insert=(cx + side * 36 - 8, top + 28), size=(16, bottom - top - 30), rx=5, fill=secondary, stroke=LINE, stroke_width=2))
        dwg.add(dwg.rect(insert=(cx - 58, top + 116), size=(116, bottom - top - 112), rx=10, fill=lighter(primary, 10), stroke=LINE, stroke_width=2))
    elif spec.style == "apron":
        dwg.add(dwg.polygon(points=[(cx - 54, top + 44), (cx + 54, top + 44), (cx + 68, bottom - 12), (cx - 68, bottom - 12)], **attrs(secondary, LINE, 3)))
        line(dwg, (cx - 54, top + 44), (cx - 92, top + 20), LINE, 2)
        line(dwg, (cx + 54, top + 44), (cx + 92, top + 20), LINE, 2)
    elif spec.style == "dress":
        dwg.add(dwg.polygon(points=[(cx - 54, top + 74), (cx + 54, top + 74), (cx + waist / 2 + 18, bottom + 40), (cx - waist / 2 - 18, bottom + 40)], **attrs(primary, LINE, 3)))
        for x in range(round(cx - 55), round(cx + 56), 24):
            line(dwg, (x, top + 82), (x + 10, bottom + 28), darker(primary, 34), 2)
    elif spec.style == "sweater":
        for y in range(top + 62, bottom - 18, 31):
            line(dwg, (cx - shoulder / 2 + 18, y), (cx + shoulder / 2 - 18, y), secondary, 7)
    elif spec.style == "utility":
        for side in (-1, 1):
            dwg.add(dwg.rect(insert=(cx + side * 34 - 22, top + 86), size=(44, 42), rx=6, fill=darker(primary, 15), stroke=LINE, stroke_width=2))
            dwg.add(dwg.rect(insert=(cx + side * 32 - 18, bottom - 72), size=(36, 36), rx=5, fill=lighter(primary, 12), stroke=LINE, stroke_width=2))
    elif spec.style == "crop":
        dwg.add(dwg.rect(insert=(cx - waist / 2 - 8, bottom - 28), size=(waist + 16, 24), rx=4, fill=darker(primary, 22), stroke=LINE, stroke_width=2))
    elif spec.style == "tunic":
        dwg.add(dwg.polygon(points=[(cx - 62, bottom - 34), (cx + 62, bottom - 34), (cx + 80, bottom + 28), (cx - 80, bottom + 28)], **attrs(lighter(primary, 8), LINE, 3)))
    elif spec.style == "vest":
        for side in (-1, 1):
            dwg.add(dwg.polygon(points=[(cx + side * 14, top + 34), (cx + side * 72, top + 38), (cx + side * 48, bottom - 14), (cx + side * 10, bottom - 10)], **attrs(darker(primary, 16), LINE, 2.5)))
    else:
        for y in range(top + 70, bottom - 20, 44):
            line(dwg, (cx - shoulder / 2 + 28, y), (cx + shoulder / 2 - 28, y), lighter(primary, 28), 2)

    line(dwg, (cx, top + 48), (cx, bottom - 12), darker(primary, 42), 2.5)
    for y in range(top + 84, bottom - 24, 38):
        dwg.add(dwg.circle(center=(cx + 8, y), r=4, fill=darker(primary, 64), stroke=LINE, stroke_width=1))
    dwg.save()


def leg_geometry(spec: LegSpec) -> tuple[int, int, int, int]:
    waist_y = {"short": 408, "average": 396, "tall": 382}[spec.height]
    shoe_y = {"short": 620, "average": 636, "tall": 658}[spec.height]
    hip = {"thin": 104, "average": 126, "strong": 150, "soft": 162}[spec.build]
    leg_w = {"thin": 31, "average": 39, "strong": 48, "soft": 54}[spec.build]
    return waist_y, shoe_y, hip, leg_w


def draw_legs(path_out: Path, index: int):
    spec = LEGS[index]
    dwg = drawing(path_out)
    cx = 256
    waist_y, shoe_y, hip, leg_w = leg_geometry(spec)
    primary, secondary, skin = spec.primary, spec.secondary, SKINS[spec.skin]

    dwg.add(dwg.rect(insert=(cx - hip / 2, waist_y - 10), size=(hip, 24), rx=7, **attrs(darker(primary, 18), LINE, 2)))

    if spec.style in {"skirt", "longskirt"}:
        skirt_h = 88 if spec.style == "skirt" else shoe_y - waist_y - 42
        flare = 30 if spec.build != "thin" else 18
        dwg.add(dwg.polygon(points=[(cx - hip / 2, waist_y), (cx + hip / 2, waist_y), (cx + hip / 2 + flare, waist_y + skirt_h), (cx - hip / 2 - flare, waist_y + skirt_h)], **attrs(primary, LINE, 3)))
        for x in range(round(cx - hip / 2 + 14), round(cx + hip / 2 + 8), 24):
            line(dwg, (x, waist_y + 8), (x + 9, waist_y + skirt_h - 8), darker(primary, 36), 2)
        if spec.style == "skirt":
            for side in (-1, 1):
                x = cx + side * 34
                dwg.add(dwg.rect(insert=(x - leg_w / 3, waist_y + skirt_h - 4), size=(leg_w * 0.66, shoe_y - waist_y - skirt_h - 18), rx=12, **attrs(skin, LINE, 2)))
    elif spec.style == "shorts":
        for side in (-1, 1):
            x = cx + side * (hip / 4)
            dwg.add(dwg.rect(insert=(x - leg_w * 0.85, waist_y), size=(leg_w * 1.7, 80), rx=10, **attrs(primary, LINE, 3)))
            dwg.add(dwg.rect(insert=(x - leg_w * 0.34, waist_y + 76), size=(leg_w * 0.68, shoe_y - waist_y - 104), rx=12, **attrs(skin, LINE, 2)))
    else:
        wide = spec.style in {"wide", "cargo", "jogger", "bootcut"}
        bottom_w = leg_w + (18 if spec.style in {"wide", "bootcut"} else 4)
        top_w = leg_w + (18 if wide else 4)
        for side in (-1, 1):
            x = cx + side * (hip / 4)
            dwg.add(dwg.polygon(points=[(x - top_w / 2, waist_y), (x + top_w / 2, waist_y), (x + bottom_w / 2, shoe_y - 25), (x - bottom_w / 2, shoe_y - 25)], **attrs(primary, LINE, 3)))
            line(dwg, (x + side * 7, waist_y + 26), (x + side * 12, shoe_y - 40), darker(primary, 38), 2)
            if spec.style == "cargo":
                dwg.add(dwg.rect(insert=(x - side * 8 - 13, waist_y + 95), size=(26, 34), rx=4, fill=lighter(primary, 8), stroke=LINE, stroke_width=2))
            if spec.style == "jogger":
                line(dwg, (x - bottom_w / 2 + 4, shoe_y - 36), (x + bottom_w / 2 - 4, shoe_y - 36), darker(primary, 55), 5)
        line(dwg, (cx, waist_y + 8), (cx, shoe_y - 38), darker(primary, 55), 3)

    for side in (-1, 1):
        x = cx + side * (hip / 4 + 8)
        shoe_w = 30 if spec.build == "thin" else 38 if spec.build == "average" else 44
        dwg.add(dwg.ellipse(center=(x, shoe_y - 12), r=(shoe_w, 15), **attrs(secondary, LINE, 3)))
        line(dwg, (x - shoe_w + 8, shoe_y - 12), (x + shoe_w - 8, shoe_y - 12), WHITE, 3)
    dwg.save()


DRAWERS = {"head": draw_head, "arms": draw_arms, "torso": draw_torso, "legs": draw_legs}


def generate():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for part, spec in PARTS.items():
        folder = OUT_ROOT / spec.folder
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.glob("*.svg"):
            old.unlink()
        for index in range(COUNT):
            DRAWERS[part](folder / f"{spec.prefix}{index}.svg", index)
        print(f"{part}: {COUNT}")


if __name__ == "__main__":
    generate()
