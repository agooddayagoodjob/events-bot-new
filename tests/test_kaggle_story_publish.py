from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import types

import pytest


ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = ROOT / "kaggle" / "CrumpleVideo" / "story_publish.py"
SPEC = importlib.util.spec_from_file_location("test_story_publish_helper", HELPER_PATH)
assert SPEC and SPEC.loader
sys.modules.setdefault("cv2", types.SimpleNamespace(VideoCapture=lambda *_args, **_kwargs: None))
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)


def test_story_safe_video_transcodes_even_if_canvas_is_already_story_size(
    monkeypatch,
    tmp_path: Path,
) -> None:
    src = tmp_path / "input.mp4"
    src.write_bytes(b"input")
    output_dir = tmp_path / "out"
    commands: list[list[str]] = []

    def fake_dimensions(path: Path) -> tuple[int, int]:
        if path.name == helper.STORY_SAFE_VIDEO_FILENAME:
            return (helper.STORY_VIDEO_WIDTH, helper.STORY_VIDEO_HEIGHT)
        return (helper.STORY_VIDEO_WIDTH, helper.STORY_VIDEO_HEIGHT)

    def fake_run(cmd, capture_output=None, text=None, check=None):  # noqa: ANN001,ARG001
        commands.append(cmd)
        story_path = output_dir / helper.STORY_SAFE_VIDEO_FILENAME
        story_path.parent.mkdir(parents=True, exist_ok=True)
        story_path.write_bytes(b"x" * 1024)
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(helper, "_ffmpeg_available", lambda: True)
    monkeypatch.setattr(helper, "_video_dimensions", fake_dimensions)
    monkeypatch.setattr(helper, "_video_probe", lambda path: {"path": str(path), "size_bytes": 1024})
    monkeypatch.setattr(helper.subprocess, "run", fake_run)

    story_path = helper._ensure_story_safe_video(
        src,
        output_dir=output_dir,
        log=lambda *_args, **_kwargs: None,
    )

    assert story_path == output_dir / helper.STORY_SAFE_VIDEO_FILENAME
    assert story_path != src
    assert commands
    ffmpeg_cmd = commands[0]
    assert ffmpeg_cmd[:4] == ["ffmpeg", "-y", "-i", str(src)]
    assert ffmpeg_cmd[ffmpeg_cmd.index("-vf") + 1] == "setsar=1"
    assert ffmpeg_cmd[ffmpeg_cmd.index("-c:v") + 1] == "libx264"
    assert ffmpeg_cmd[ffmpeg_cmd.index("-preset") + 1] == helper.STORY_VIDEO_PRESET
    assert ffmpeg_cmd[ffmpeg_cmd.index("-b:v") + 1] == helper.STORY_VIDEO_BITRATE
    assert ffmpeg_cmd[ffmpeg_cmd.index("-maxrate") + 1] == helper.STORY_VIDEO_MAXRATE
    assert ffmpeg_cmd[ffmpeg_cmd.index("-bufsize") + 1] == helper.STORY_VIDEO_BUFSIZE
    assert ffmpeg_cmd[ffmpeg_cmd.index("-tag:v") + 1] == "avc1"
    assert ffmpeg_cmd[ffmpeg_cmd.index("-c:a") + 1] == "aac"
    assert ffmpeg_cmd[ffmpeg_cmd.index("-b:a") + 1] == "128k"
    assert "-shortest" in ffmpeg_cmd


def test_story_safe_video_scales_and_pads_non_story_canvas(
    monkeypatch,
    tmp_path: Path,
) -> None:
    src = tmp_path / "input.mov"
    src.write_bytes(b"input")
    output_dir = tmp_path / "out"
    commands: list[list[str]] = []

    def fake_dimensions(path: Path) -> tuple[int, int]:
        if path.name == helper.STORY_SAFE_VIDEO_FILENAME:
            return (helper.STORY_VIDEO_WIDTH, helper.STORY_VIDEO_HEIGHT)
        return (1080, 1920)

    def fake_run(cmd, capture_output=None, text=None, check=None):  # noqa: ANN001,ARG001
        commands.append(cmd)
        story_path = output_dir / helper.STORY_SAFE_VIDEO_FILENAME
        story_path.parent.mkdir(parents=True, exist_ok=True)
        story_path.write_bytes(b"x" * 1024)
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(helper, "_ffmpeg_available", lambda: True)
    monkeypatch.setattr(helper, "_video_dimensions", fake_dimensions)
    monkeypatch.setattr(helper, "_video_probe", lambda path: {"path": str(path), "size_bytes": 1024})
    monkeypatch.setattr(helper.subprocess, "run", fake_run)

    helper._ensure_story_safe_video(
        src,
        output_dir=output_dir,
        log=lambda *_args, **_kwargs: None,
    )

    ffmpeg_cmd = commands[0]
    filter_graph = ffmpeg_cmd[ffmpeg_cmd.index("-vf") + 1]
    assert "scale=720:1280:force_original_aspect_ratio=decrease:flags=lanczos" in filter_graph
    assert "pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=black" in filter_graph


def test_story_report_includes_media_probe(monkeypatch, tmp_path: Path) -> None:
    src = tmp_path / "story.mp4"
    src.write_bytes(b"video")
    monkeypatch.setattr(helper, "_video_probe", lambda path: {"path": str(path), "width": 720})

    report = helper._build_story_report(
        {"mode": "video", "pinned": True},
        phase="publish",
        account={"id": 1, "username": "story"},
        media_path=src,
    )

    assert report["media_path"] == str(src)
    assert report["media"] == {"path": str(src), "width": 720}


def test_validate_native_story_video_accepts_hevc_render(monkeypatch, tmp_path: Path) -> None:
    src = tmp_path / "final.mp4"
    src.write_bytes(b"video")
    monkeypatch.setattr(
        helper,
        "_video_probe",
        lambda path: {
            "path": str(path),
            "size_bytes": 9 * 1024 * 1024,
            "width": 720,
            "height": 1280,
            "fps": 30.0,
            "duration_seconds": 53.0,
            "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
            "video_codec": "hevc",
            "video_tag": "hvc1",
            "pix_fmt": "yuv420p",
            "audio_codec": "aac",
            "audio_sample_rate": 48000,
            "audio_channels": 2,
            "approx_bitrate_kbps": 1428.0,
        },
    )

    validated = helper._validate_native_story_video(src, log=lambda *_args, **_kwargs: None)

    assert validated == src


def test_validate_native_story_video_rejects_non_native_profile(monkeypatch, tmp_path: Path) -> None:
    src = tmp_path / "final.mp4"
    src.write_bytes(b"video")
    monkeypatch.setattr(
        helper,
        "_video_probe",
        lambda path: {
            "path": str(path),
            "size_bytes": 4 * 1024 * 1024,
            "width": 720,
            "height": 1280,
            "fps": 30.0,
            "duration_seconds": 53.0,
            "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
            "video_codec": "h264",
            "video_tag": "avc1",
            "pix_fmt": "yuv420p",
            "audio_codec": "aac",
            "audio_sample_rate": 44100,
            "audio_channels": 2,
        },
    )

    with pytest.raises(RuntimeError, match="native Telegram-ready final mp4"):
        helper._validate_native_story_video(src, log=lambda *_args, **_kwargs: None)
