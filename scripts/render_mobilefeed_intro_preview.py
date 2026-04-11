from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageColor, ImageDraw

ROOT = Path("/workspaces/events-bot-new")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.render_mobilefeed_intro_still import (
    BLENDER,
    BLENDER_SCRIPT,
    CONFIG_DIR,
    FOCUS_EVENT_ID,
    POSTERS,
    TEXTURE_DIR,
    VARIANTS,
    atlas_and_meta,
    build_variant_config,
    ensure_dirs,
    make_overlay_texture,
    make_screen_label_texture,
    make_screen_texture,
    make_shadow_texture,
)

OUT_DIR = ROOT / "artifacts" / "codex" / "mobilefeed_intro_anim_preview"
RAW_FRAMES_DIR = OUT_DIR / "frames_raw"
SPARSE_FRAMES_DIR = OUT_DIR / "frames_sparse"
INTERP_FRAMES_DIR = OUT_DIR / "frames_interp"
FRAMES_DIR = OUT_DIR / "frames"
PREVIEW_W = 540
PREVIEW_H = 960
FPS = 30
RENDER_FRAME_STEP = 4
FRAME_START = 1
RAW_FRAME_END = 102
PREVIEW_FRAME_END = 114
ACTIVE_VARIANT = VARIANTS[0]
SYNC_START_FRAME = 82
CUT_FRAME = 103
TAIL_LABEL_END = 103
SCENE1_TAIL_START = 1.439
SCENE1_TAIL_END = 1.806
BG_FADE_START = CUT_FRAME
BG_FADE_END = PREVIEW_FRAME_END
BG_LIGHT = ImageColor.getrgb("#F8F6F2")
BG_DARK = ImageColor.getrgb("#000000")


def ease_out_cubic(t: float):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def ease_in_out_cubic(t: float):
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 4.0 * t * t * t
    return 1.0 - ((-2.0 * t + 2.0) ** 3) / 2.0


def ease_in_out_quint(t: float):
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 16.0 * t**5
    return 1.0 - ((-2.0 * t + 2.0) ** 5) / 2.0


def lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float):
    t = max(0.0, min(1.0, t))
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def prepare_dirs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    SPARSE_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    INTERP_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for directory in (RAW_FRAMES_DIR, SPARSE_FRAMES_DIR, INTERP_FRAMES_DIR, FRAMES_DIR):
        for child in directory.glob("*.png"):
            child.unlink()


def render_animation():
    ensure_dirs()
    prepare_dirs()
    atlas_path, ribbon_meta = atlas_and_meta()
    shadow_path = TEXTURE_DIR / "mobilefeed_shadow.png"
    make_shadow_texture(shadow_path)

    overlay_path = TEXTURE_DIR / f"{ACTIVE_VARIANT.slug}_preview_overlay.png"
    screen_path = TEXTURE_DIR / f"{ACTIVE_VARIANT.slug}_preview_screen.png"
    screen_top_label_path = TEXTURE_DIR / f"{ACTIVE_VARIANT.slug}_preview_screen_top.png"
    screen_bottom_label_path = TEXTURE_DIR / f"{ACTIVE_VARIANT.slug}_preview_screen_bottom.png"
    config_path = CONFIG_DIR / f"{ACTIVE_VARIANT.slug}_preview_anim.json"
    output_anchor = OUT_DIR / "handoff_anchor.png"

    make_overlay_texture(ACTIVE_VARIANT, overlay_path)
    make_screen_texture(ACTIVE_VARIANT, screen_path)
    make_screen_label_texture(ACTIVE_VARIANT.screen_top, screen_top_label_path, position="top")
    make_screen_label_texture(ACTIVE_VARIANT.screen_bottom, screen_bottom_label_path, position="bottom")

    cfg = build_variant_config(
        ACTIVE_VARIANT,
        atlas_path=atlas_path,
        ribbon_meta=ribbon_meta,
        shadow_path=shadow_path,
        overlay_path=overlay_path,
        screen_path=screen_path,
        screen_top_label_path=screen_top_label_path,
        screen_bottom_label_path=screen_bottom_label_path,
        output_path=output_anchor,
    )
    cfg.update(
        {
            "res_x": PREVIEW_W,
            "res_y": PREVIEW_H,
            "samples": 1,
            "use_denoising": True,
            "backdrop_color": "#F8F6F2",
            "camera_background_color": "#F8F6F2",
            "camera_location": (2.42, -4.30, 4.02),
            "camera_target": (0.04, -0.66, 0.05),
            "camera_lens_mm": 60.0,
            "key_light_energy": 1380,
            "fill_light_energy": 300,
            "top_light_energy": 180,
            "render_animation": True,
            "output_pattern": str(RAW_FRAMES_DIR / "frame_"),
            "animation": {
                "fps": FPS,
                "frame_step": RENDER_FRAME_STEP,
                "frame_start": FRAME_START,
                "frame_end": RAW_FRAME_END,
                "combo_mid_frame": 44,
                "sync_start_frame": SYNC_START_FRAME,
                "sync_mid_frame": 96,
                "combo_lens_mm": 62.0,
                "sync_start_lens_mm": 70.0,
                "sync_mid_lens_mm": 80.0,
                "end_lens_mm": 84.0,
                "combo_fill": 0.40,
                "sync_start_fill": 0.62,
                "sync_mid_fill": 0.84,
                "scene1_end_scale": 0.986,
                "combo_height_offset": 0.16,
                "combo_side_offset": 0.010,
                "sync_start_height_offset": 0.072,
                "sync_start_side_offset": 0.004,
                "sync_mid_height_offset": 0.020,
                "sync_mid_side_offset": 0.000,
                "end_height_offset": 0.000,
                "start_up_blend": 0.10,
                "combo_up_blend": 0.56,
                "sync_up_blend": 0.94,
                "focus_target_normal_offset": 0.010,
                "screen_bottom_label_exit_start": 88,
                "screen_bottom_label_exit_end": 96,
                "screen_top_label_exit_start": 92,
                "screen_top_label_exit_end": 101,
            },
        }
    )
    config_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run(
        [
            str(BLENDER),
            "-b",
            "-P",
            str(BLENDER_SCRIPT),
            "--",
            "--config",
            str(config_path),
        ],
        check=True,
    )
    ffmpeg = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()
    sparse_sources = sorted(RAW_FRAMES_DIR.glob("frame_*.png"))
    if not sparse_sources:
        raise RuntimeError("No sparse intro frames were rendered")
    for idx, source in enumerate(sparse_sources, start=1):
        shutil.copy2(source, SPARSE_FRAMES_DIR / f"frame_{idx:04d}.png")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-framerate",
            str(FPS / RENDER_FRAME_STEP),
            "-i",
            str(SPARSE_FRAMES_DIR / "frame_%04d.png"),
            "-vf",
            "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
            str(INTERP_FRAMES_DIR / "frame_%04d.png"),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return {
        "overlay": overlay_path,
        "screen_top_label": screen_top_label_path,
        "screen_bottom_label": screen_bottom_label_path,
    }


def composite_overlay(assets: dict[str, Path]):
    overlay_path = assets["overlay"]
    overlay_im = Image.open(overlay_path).convert("RGBA").resize((PREVIEW_W, PREVIEW_H), Image.Resampling.LANCZOS)
    raw_frames = {int(path.stem.split("_")[-1]): path for path in INTERP_FRAMES_DIR.glob("frame_*.png")}
    for i in range(FRAME_START, PREVIEW_FRAME_END + 1):
        reference_im = make_scene1_reference_for_frame(i)
        frame_path = raw_frames.get(i)
        if frame_path and i < CUT_FRAME:
            with Image.open(frame_path).convert("RGBA") as frame:
                canvas = frame.copy()
        else:
            canvas = reference_im.copy()

        if frame_path and i <= 18:
            if i <= 6:
                alpha = 1.0
                dy = 0
            else:
                prog = ease_in_out_cubic((i - 6) / 12.0)
                alpha = 1.0 - prog
                dy = round(-56 * prog)
            overlay = overlay_im.copy()
            alpha_channel = overlay.getchannel("A").point(lambda v: int(v * alpha))
            overlay.putalpha(alpha_channel)
            layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            layer.alpha_composite(overlay, (0, dy))
            canvas = Image.alpha_composite(canvas, layer)

        out_path = FRAMES_DIR / f"frame_{i:04d}.png"
        canvas.save(out_path)


def make_storyboard():
    selected = [1, 8, 16, 24, 34, 41, 42, 50, PREVIEW_FRAME_END]
    thumbs = []
    for frame in selected:
        path = FRAMES_DIR / f"frame_{frame:04d}.png"
        with Image.open(path).convert("RGB") as image:
            thumbs.append((frame, image.resize((220, round(220 * image.height / image.width)), Image.Resampling.LANCZOS)))
    label_h = 44
    margin = 28
    max_h = max(im.height for _, im in thumbs)
    canvas = Image.new("RGB", (margin + len(thumbs) * (220 + margin), margin * 2 + max_h + label_h), ImageColor.getrgb("#F1ECE5"))
    draw = ImageDraw.Draw(canvas)
    x = margin
    for frame, thumb in thumbs:
        canvas.paste(thumb, (x, margin))
        draw.text((x, margin + max_h + 10), f"f{frame}", fill=ImageColor.getrgb("#11110F"))
        x += 220 + margin
    out = OUT_DIR / "storyboard.png"
    canvas.save(out)
    return out


def scene1_tail_time_for_frame(frame_num: int) -> float:
    if frame_num < CUT_FRAME:
        return SCENE1_TAIL_START
    prog = (frame_num - CUT_FRAME) / max(1.0, PREVIEW_FRAME_END - CUT_FRAME)
    return SCENE1_TAIL_START + (SCENE1_TAIL_END - SCENE1_TAIL_START) * prog


def scene1_geometry(scene_t: float):
    poster = POSTERS[FOCUS_EVENT_ID]
    with Image.open(poster.image_path).convert("RGBA") as image:
        if scene_t < 0.45:
            scale = 0.4 + (0.5 * ease_out_cubic(scene_t / 0.45))
            top = None
        elif scene_t < 1.65:
            scale = 0.9 + (0.1 * ((scene_t - 0.45) / 1.2))
            top = None
        else:
            scale = 1.0
            prog = min(1.0, (scene_t - 1.65) / 0.75)
            split_y = int(PREVIEW_H * 0.6)
            sy = PREVIEW_H / 2
            ey = split_y / 2
            base_h = round(PREVIEW_W * image.height / image.width)
            top = int(sy + (ey - sy) * ease_in_out_quint(prog) - base_h / 2)
        poster_w = round(PREVIEW_W * scale)
        poster_h = round(poster_w * image.height / image.width)
        x = (PREVIEW_W - poster_w) // 2
        y = (PREVIEW_H - poster_h) // 2 if top is None else top
        return {
            "x": x,
            "y": y,
            "w": poster_w,
            "h": poster_h,
        }


def background_color_for_frame(frame_num: int):
    if frame_num <= BG_FADE_START:
        return BG_LIGHT
    if frame_num >= BG_FADE_END:
        return BG_DARK
    prog = ease_in_out_cubic((frame_num - BG_FADE_START) / max(1.0, BG_FADE_END - BG_FADE_START))
    return lerp_color(BG_LIGHT, BG_DARK, prog)


def render_scene1_reference(scene_t: float, *, frame_num: int):
    poster = POSTERS[FOCUS_EVENT_ID]
    with Image.open(poster.image_path).convert("RGBA") as image:
        bg = background_color_for_frame(frame_num)
        canvas = Image.new("RGBA", (PREVIEW_W, PREVIEW_H), (*bg, 255))
        geometry = scene1_geometry(scene_t)
        poster_w = geometry["w"]
        poster_h = geometry["h"]
        resized = image.resize((poster_w, poster_h), Image.Resampling.LANCZOS)
        x = geometry["x"]
        y = geometry["y"]
        canvas.alpha_composite(resized, (x, y))
        return canvas


def make_scene1_reference_for_frame(frame_num: int):
    return render_scene1_reference(scene1_tail_time_for_frame(frame_num), frame_num=frame_num)


def tail_label_alpha(frame_num: int) -> float:
    if frame_num < CUT_FRAME:
        return 0.0
    if frame_num >= TAIL_LABEL_END:
        return 0.0
    prog = (frame_num - CUT_FRAME) / max(1.0, TAIL_LABEL_END - CUT_FRAME)
    return 1.0 - ease_in_out_cubic(prog)


def _with_alpha(image: Image.Image, alpha: float) -> Image.Image:
    layer = image.copy()
    alpha_channel = layer.getchannel("A").point(lambda v: int(v * max(0.0, min(1.0, alpha))))
    layer.putalpha(alpha_channel)
    return layer


def composite_tail_labels(canvas: Image.Image, frame_num: int, top_label_im: Image.Image, bottom_label_im: Image.Image):
    alpha = tail_label_alpha(frame_num)
    if alpha <= 0:
        return canvas

    scene_t = scene1_tail_time_for_frame(frame_num)
    geometry = scene1_geometry(scene_t)
    poster_x = geometry["x"]
    poster_y = geometry["y"]
    poster_w = geometry["w"]
    poster_h = geometry["h"]

    top_target_w = min(PREVIEW_W - 56, round(poster_w * 0.90))
    top_target_h = round(top_target_w * top_label_im.height / top_label_im.width)
    top_x = max(24, poster_x + round(poster_w * 0.04))
    top_y = max(24, poster_y - top_target_h - 20)

    bottom_target_w = min(PREVIEW_W - 76, round(poster_w * 0.76))
    bottom_target_h = round(bottom_target_w * bottom_label_im.height / bottom_label_im.width)
    bottom_x = max(34, poster_x + round(poster_w * 0.08))
    bottom_y = min(PREVIEW_H - bottom_target_h - 32, poster_y + poster_h + 18)

    top_layer = _with_alpha(top_label_im.resize((top_target_w, top_target_h), Image.Resampling.LANCZOS), alpha)
    bottom_layer = _with_alpha(bottom_label_im.resize((bottom_target_w, bottom_target_h), Image.Resampling.LANCZOS), alpha)

    out = canvas.copy()
    out.alpha_composite(top_layer, (top_x, top_y))
    out.alpha_composite(bottom_layer, (bottom_x, bottom_y))
    return out


def write_reference_frames():
    sync_start = render_scene1_reference(SCENE1_TAIL_START, frame_num=CUT_FRAME)
    sync_start_out = OUT_DIR / "expected_sync_start_2d_frame.png"
    sync_start.save(sync_start_out)
    zoom_end = render_scene1_reference(SCENE1_TAIL_END, frame_num=PREVIEW_FRAME_END)
    zoom_end_out = OUT_DIR / "expected_zoom_end_2d_frame.png"
    zoom_end.save(zoom_end_out)
    return sync_start_out, zoom_end_out


def encode_preview():
    ffmpeg = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()
    if ffmpeg:
        mp4_path = OUT_DIR / "mobilefeed_intro_preview.mp4"
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-framerate",
                str(FPS),
                "-i",
                str(FRAMES_DIR / "frame_%04d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(mp4_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return mp4_path

    gif_path = OUT_DIR / "mobilefeed_intro_preview.gif"
    frames = []
    for frame_path in sorted(FRAMES_DIR.glob("frame_*.png")):
        frames.append(Image.open(frame_path).convert("P", palette=Image.Palette.ADAPTIVE))
    if not frames:
        raise RuntimeError("No composited frames found for GIF export")
    first, *rest = frames
    first.save(
        gif_path,
        save_all=True,
        append_images=rest,
        duration=round(1000 / FPS),
        loop=0,
        disposal=2,
    )
    return gif_path


def main():
    assets = render_animation()
    composite_overlay(assets)
    shutil.copy2(FRAMES_DIR / f"frame_{PREVIEW_FRAME_END:04d}.png", OUT_DIR / "handoff_last_frame.png")
    storyboard = make_storyboard()
    sync_start_ref, zoom_end_ref = write_reference_frames()
    preview_path = encode_preview()
    print(preview_path)
    print(storyboard)
    print(sync_start_ref)
    print(zoom_end_ref)


if __name__ == "__main__":
    main()
