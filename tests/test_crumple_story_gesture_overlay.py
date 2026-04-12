from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "kaggle"
    / "CrumpleVideo"
    / "story_gesture_overlay.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("crumple_story_gesture_overlay", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_story_gesture_overlay_draws_cta_in_visible_gap():
    overlay = _load_module()
    width, height = 1080, 1572
    frame = overlay._background_frame(width, height)
    yy, xx = np.ogrid[:height, :width]
    cy = int(height * 0.52)
    cx = width // 2
    outer = (xx - cx) ** 2 + (yy - cy) ** 2 <= 150**2
    inner = (xx - cx) ** 2 + (yy - cy) ** 2 <= 110**2
    frame[outer] = (205, 202, 196)
    frame[inner] = (232, 228, 222)

    rendered = overlay.apply_story_gesture_frame(
        frame,
        step_index=0,
        frame_index=8,
        total_frames=30,
    )

    diff = np.abs(rendered.astype(np.int16) - frame.astype(np.int16)).sum(axis=2)
    assert np.count_nonzero(diff[int(height * 0.68) :, : int(width * 0.72)] > 30) > 1200


def test_story_gesture_overlay_stays_under_paper_mask():
    overlay = _load_module()
    width, height = 1080, 1572
    frame = overlay._background_frame(width, height)
    frame[int(height * 0.62) :, :] = (228, 224, 218)

    rendered = overlay.apply_story_gesture_frame(
        frame,
        step_index=0,
        frame_index=8,
        total_frames=30,
    )

    diff = np.abs(rendered.astype(np.int16) - frame.astype(np.int16)).sum(axis=2)
    covered_region = diff[int(height * 0.76) :, : int(width * 0.70)]
    assert covered_region.max() < 10
