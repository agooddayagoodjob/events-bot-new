from __future__ import annotations

import numpy as np
from pathlib import Path

from PIL import Image

from video_announce.video_afisha_2d import VideoAfisha2DConfig, create_advanced_scene


def test_create_advanced_scene_keeps_late_drift_moving_each_30fps_frame(
    tmp_path: Path,
) -> None:
    poster_path = tmp_path / "poster.png"
    gradient = Image.new("RGBA", (64, 64))
    for x in range(64):
        for y in range(64):
            gradient.putpixel((x, y), ((x * 4) % 256, (y * 4) % 256, 128, 255))
    gradient.save(poster_path)

    clip = create_advanced_scene(
        poster_path,
        {
            "title": "Scene 1",
            "date": "12 апреля",
            "location": "Калининград",
        },
        config=VideoAfisha2DConfig(
            width=270,
            height=480,
            font_path=None,
        ),
    )

    frame_a = clip.get_frame(2.8)
    frame_b = clip.get_frame(2.8 + (1.0 / 30.0))

    assert float(np.abs(frame_a.astype(np.int16) - frame_b.astype(np.int16)).mean()) > 0.2
