from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


@dataclass(frozen=True)
class GestureStep:
    headline: str
    subline: str
    show_touch_cue: bool = False


GESTURE_STEPS: tuple[GestureStep, ...] = (
    GestureStep("Нажми и держи", "чтобы читать", show_touch_cue=True),
    GestureStep("Держишь палец", "афиша на паузе"),
    GestureStep("Веди по экрану", "чтобы промотать", show_touch_cue=True),
)
GESTURE_STEP_COUNT = len(GESTURE_STEPS)

_FONT_PATHS: dict[str, Path | None] = {}
_FONT_LOGGED = False
_BACKGROUND_COLOR = (20, 20, 25)


def _font_candidates(search_roots: list[Path] | None, names: tuple[str, ...]) -> list[Path]:
    candidates: list[Path] = []
    seen: set[Path] = set()
    roots = list(search_roots or [])
    roots.extend(
        [
            Path.cwd(),
            Path("/kaggle/working"),
            Path("/kaggle/working/assets"),
            Path("/kaggle/working/ro_znanie_fonts"),
            Path("/kaggle/working/assets/ro_znanie_fonts"),
        ]
    )

    for root in roots:
        for base in (root, root / "assets", root / "ro_znanie_fonts", root / "assets" / "ro_znanie_fonts"):
            if base in seen:
                continue
            seen.add(base)
            for name in names:
                candidate = base / name
                if candidate.exists():
                    candidates.append(candidate)

    inp = Path("/kaggle/input")
    if inp.exists():
        for name in names:
            for pattern in (
                f"*/{name}",
                f"*/assets/{name}",
                f"*/ro_znanie_fonts/{name}",
                f"*/assets/ro_znanie_fonts/{name}",
            ):
                candidates.extend(inp.glob(pattern))

    candidates.extend(
        [
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"),
        ]
    )
    return [path for path in candidates if path.exists()]


def _font_supports_cyrillic(font: ImageFont.FreeTypeFont) -> bool:
    for ch in ("Я", "Ж", "Ю", "П"):
        try:
            bbox = font.getbbox(ch)
        except Exception:
            return False
        if not bbox or (bbox[2] - bbox[0]) <= 0:
            return False
    return True


def _pick_font_path(role: str, *, search_roots: list[Path] | None = None) -> Path | None:
    names = {
        "headline": (
            "Cygre-Medium.ttf",
            "Cygre-SemiBold.ttf",
            "Cygre-Bold.ttf",
            "Cygre-Regular.ttf",
        ),
        "subline": (
            "Cygre-Regular.ttf",
            "Cygre-Book.ttf",
            "Cygre-Medium.ttf",
        ),
    }.get(role, ("Cygre-Regular.ttf",))

    for candidate in _font_candidates(search_roots, names):
        try:
            font = ImageFont.truetype(str(candidate), 32)
        except Exception:
            continue
        if _font_supports_cyrillic(font):
            return candidate
    return None


def _load_font(
    role: str,
    size: int,
    *,
    search_roots: list[Path] | None = None,
) -> ImageFont.FreeTypeFont:
    global _FONT_LOGGED

    path = _FONT_PATHS.get(role)
    if path is None and role not in _FONT_PATHS:
        path = _pick_font_path(role, search_roots=search_roots)
        _FONT_PATHS[role] = path

    if path is not None:
        try:
            font = ImageFont.truetype(str(path), int(size))
            if not _FONT_LOGGED:
                _FONT_LOGGED = True
                print(f"✅ Story gesture font: {path}")
            return font
        except Exception:
            pass

    for fallback in (
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"),
    ):
        if fallback.exists():
            return ImageFont.truetype(str(fallback), int(size))
    return ImageFont.load_default()


def _ease_out_cubic(value: float) -> float:
    t = max(0.0, min(1.0, float(value)))
    return 1.0 - ((1.0 - t) ** 3)


def _scale_alpha(color: tuple[int, int, int, int], scale: float) -> tuple[int, int, int, int]:
    alpha = max(0, min(255, int(round(color[3] * max(0.0, min(1.0, scale))))))
    return color[0], color[1], color[2], alpha


def _background_frame(width: int, height: int) -> np.ndarray:
    if width <= 0 or height <= 0:
        return np.zeros((0, 0, 3), dtype=np.uint8)
    gradient = np.linspace(0.8, 1.0, num=height, dtype=np.float32)[:, None, None]
    base = np.array(_BACKGROUND_COLOR, dtype=np.float32)[None, None, :]
    bg = np.clip(base * gradient, 0, 255).astype(np.uint8)
    return np.repeat(bg, width, axis=1)


def _paper_mask(frame_rgb: np.ndarray) -> np.ndarray:
    height, width = frame_rgb.shape[:2]
    bg = _background_frame(width, height)
    diff = np.abs(frame_rgb.astype(np.int16) - bg.astype(np.int16)).sum(axis=2).astype(np.uint16)
    mask = Image.fromarray(np.where(diff > 28, 255, 0).astype(np.uint8)).convert("L")
    mask = mask.filter(ImageFilter.MaxFilter(7))
    mask = mask.filter(ImageFilter.MaxFilter(7))
    mask = mask.filter(ImageFilter.GaussianBlur(1.4))
    return np.asarray(mask, dtype=np.uint8)


def _draw_touch_cue(
    canvas: Image.Image,
    *,
    x: int,
    y: int,
    alpha_scale: float,
    pulse: float,
) -> Image.Image:
    outer_scale = 1.0 + (0.05 * pulse)
    mid_scale = 1.0 + (0.03 * pulse)
    cue_r_outer = int(max(32, canvas.size[0] * 0.06) * outer_scale)
    cue_r_mid = int(max(22, canvas.size[0] * 0.04) * mid_scale)
    cue_r_dot = max(10, int(canvas.size[0] * 0.018))
    finger_box = max(120, int(canvas.size[0] * 0.16))
    finger_shift = int(canvas.size[1] * 0.004 * pulse)

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    ring = _scale_alpha((242, 239, 231, 52), alpha_scale * (0.85 + (0.15 * pulse)))
    fill = _scale_alpha((242, 239, 231, 110), alpha_scale * (0.90 + (0.10 * pulse)))
    fingertip = _scale_alpha((242, 239, 231, 190), alpha_scale)

    draw.ellipse((x - cue_r_outer, y - cue_r_outer, x + cue_r_outer, y + cue_r_outer), outline=ring, width=2)
    draw.ellipse((x - cue_r_mid, y - cue_r_mid, x + cue_r_mid, y + cue_r_mid), outline=ring, width=2)
    draw.ellipse((x - cue_r_dot, y - cue_r_dot, x + cue_r_dot, y + cue_r_dot), fill=fill)

    finger = Image.new("RGBA", (finger_box, finger_box), (0, 0, 0, 0))
    finger_draw = ImageDraw.Draw(finger)
    left = int(finger_box * 0.39)
    top = int(finger_box * 0.11)
    right = int(finger_box * 0.61)
    bottom = int(finger_box * 0.76)
    finger_draw.rounded_rectangle(
        (left, top, right, bottom),
        radius=max(14, int(finger_box * 0.10)),
        fill=fingertip,
    )
    finger = finger.rotate(-28, resample=Image.Resampling.BICUBIC, expand=True)
    overlay.alpha_composite(
        finger,
        dest=(x - finger.width // 2 - max(8, int(canvas.size[0] * 0.015)), y - finger.height // 2 + finger_shift),
    )
    return Image.alpha_composite(canvas, overlay)


def _render_gesture_layer(
    size: tuple[int, int],
    *,
    step: GestureStep,
    frame_index: int,
    total_frames: int,
    search_roots: list[Path] | None = None,
) -> Image.Image:
    width, height = size
    progress = 1.0 if total_frames <= 1 else frame_index / float(max(total_frames - 1, 1))
    appear = _ease_out_cubic((frame_index + 1) / 6.0)
    settle = 1.0
    if progress > 0.82:
        settle = 1.0 - (0.15 * ((progress - 0.82) / 0.18))
    alpha_scale = max(0.0, min(1.0, appear * settle))

    pulse_progress = min(1.0, progress / 0.45) if step.show_touch_cue else 0.0
    pulse = math.sin(pulse_progress * math.pi) if step.show_touch_cue else 0.0

    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    if step.show_touch_cue:
        canvas = _draw_touch_cue(
            canvas,
            x=int(width * 0.15),
            y=int(height * 0.81),
            alpha_scale=alpha_scale,
            pulse=pulse,
        )

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    shadow = Image.new("RGBA", size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    sd = ImageDraw.Draw(shadow)

    headline_size = max(46, int(width * 0.073))
    subline_size = max(34, int(width * 0.050))
    line_gap = max(56, int(height * 0.078))
    accent_w = max(132, int(width * 0.16))
    text_x = int(width * 0.24)
    text_y = int(height * 0.74)

    headline_font = _load_font("headline", headline_size, search_roots=search_roots)
    subline_font = _load_font("subline", subline_size, search_roots=search_roots)

    shadow_color = _scale_alpha((0, 0, 0, 180), alpha_scale)
    text_color = _scale_alpha((242, 239, 231, 238), alpha_scale)
    sub_color = _scale_alpha((242, 239, 231, 210), alpha_scale)
    accent = _scale_alpha((241, 228, 75, 205), alpha_scale * 0.90)

    sd.text((text_x, text_y), step.headline, font=headline_font, fill=shadow_color)
    sd.text((text_x, text_y + line_gap), step.subline, font=subline_font, fill=shadow_color)
    shadow_blurred = shadow.filter(ImageFilter.GaussianBlur(14))
    shadow_offset = ImageChops.offset(shadow_blurred, 0, max(4, int(height * 0.005)))

    od.text((text_x, text_y), step.headline, font=headline_font, fill=text_color)
    od.text((text_x, text_y + line_gap), step.subline, font=subline_font, fill=sub_color)
    od.rounded_rectangle(
        (
            text_x,
            text_y + line_gap + subline_size + 18,
            text_x + accent_w,
            text_y + line_gap + subline_size + 24,
        ),
        radius=3,
        fill=accent,
    )

    canvas = Image.alpha_composite(canvas, shadow_offset)
    return Image.alpha_composite(canvas, overlay)


def apply_story_gesture_frame(
    frame_rgb: np.ndarray,
    *,
    step_index: int,
    frame_index: int,
    total_frames: int,
    search_roots: list[str | Path] | None = None,
) -> np.ndarray:
    if step_index < 0 or step_index >= GESTURE_STEP_COUNT:
        return frame_rgb
    if frame_rgb is None or frame_rgb.ndim != 3 or frame_rgb.shape[2] != 3:
        return frame_rgb

    roots: list[Path] = []
    if search_roots:
        for root in search_roots:
            try:
                roots.append(Path(root))
            except Exception:
                continue

    step = GESTURE_STEPS[step_index]
    original = Image.fromarray(frame_rgb.astype(np.uint8)).convert("RGBA")
    gesture_layer = _render_gesture_layer(
        (frame_rgb.shape[1], frame_rgb.shape[0]),
        step=step,
        frame_index=frame_index,
        total_frames=total_frames,
        search_roots=roots,
    )
    paper_mask = Image.fromarray(_paper_mask(frame_rgb)).convert("L")
    paper_layer = Image.composite(
        original,
        Image.new("RGBA", original.size, (0, 0, 0, 0)),
        paper_mask,
    )
    composed = Image.alpha_composite(original, gesture_layer)
    composed = Image.alpha_composite(composed, paper_layer)
    return np.asarray(composed.convert("RGB"))
