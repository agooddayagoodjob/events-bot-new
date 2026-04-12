from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NOTEBOOK_PATH = ROOT / "crumple_video.ipynb"
POSTER_MODULE_PATH = ROOT / "poster_overlay.py"
STORY_MODULE_PATH = ROOT / "story_publish.py"
GESTURE_MODULE_PATH = ROOT / "story_gesture_overlay.py"


def _replace_embedded_module(
    source: str,
    *,
    anchor: str,
    module_source: str,
) -> str:
    anchor_index = source.find(anchor)
    if anchor_index < 0:
        raise RuntimeError(f"Could not locate {anchor} in notebook")
    start = source.find("        code = ", anchor_index)
    end_marker = "\n        target.write_text(code, encoding='utf-8')"
    end = source.find(end_marker, start)
    if start < 0 or end < 0:
        raise RuntimeError(f"Could not locate embedded module block for {anchor}")
    replacement = f"        code = {module_source!r}"
    return source[:start] + replacement + source[end:]


def main() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    poster_module_source = POSTER_MODULE_PATH.read_text(encoding="utf-8").rstrip("\n")
    story_module_source = STORY_MODULE_PATH.read_text(encoding="utf-8").rstrip("\n")
    gesture_module_source = GESTURE_MODULE_PATH.read_text(encoding="utf-8").rstrip("\n")

    overlay_call_old = (
        "        overlay = scene.get(\"poster_overlay\")\n"
        "        if isinstance(overlay, dict):\n"
        "            overlay_text = overlay.get(\"text\")\n"
        "        else:\n"
        "            overlay_text = None\n"
        "        if found and isinstance(overlay_text, str) and overlay_text.strip():\n"
        "            try:\n"
        "                found = apply_poster_overlay(found, text=overlay_text, out_dir=posters_dir, search_roots=OVERLAY_FONT_ROOTS)\n"
        "            except Exception as e:\n"
        "                log(f\"⚠️ Overlay failed for scene {i}: {e}\")\n"
    )
    overlay_call_new = (
        "        overlay = scene.get(\"poster_overlay\")\n"
        "        overlay_text = None\n"
        "        highlight_title = None\n"
        "        if isinstance(overlay, dict):\n"
        "            overlay_text = overlay.get(\"text\")\n"
        "            missing = overlay.get(\"missing\")\n"
        "            if isinstance(missing, list):\n"
        "                highlight_title = \"title\" in {str(part).strip().casefold() for part in missing if isinstance(part, str)}\n"
        "        if found and isinstance(overlay_text, str) and overlay_text.strip():\n"
        "            try:\n"
        "                found = apply_poster_overlay(\n"
        "                    found,\n"
        "                    text=overlay_text,\n"
        "                    out_dir=posters_dir,\n"
        "                    search_roots=OVERLAY_FONT_ROOTS,\n"
        "                    highlight_title=highlight_title,\n"
        "                )\n"
        "            except Exception as e:\n"
        "                log(f\"⚠️ Overlay failed for scene {i}: {e}\")\n"
    )
    helper_insert_old = (
        "_ensure_story_publish_module()\n\n"
        "# Import from working dir (preferred)\n"
        "sys.path.insert(0, '/kaggle/working')\n"
        "from poster_overlay import apply_poster_overlay\n"
        "from story_publish import preflight_story_publish_from_kaggle, publish_story_from_kaggle\n"
    )
    helper_insert_new = (
        "_ensure_story_publish_module()\n\n"
        "def _ensure_story_gesture_overlay_module():\n"
        "    target = Path('/kaggle/working/story_gesture_overlay.py')\n"
        "    if target.exists():\n"
        "        return\n"
        "    try:\n"
        f"        code = {gesture_module_source!r}\n"
        "        target.write_text(code, encoding='utf-8')\n"
        "        print(f'✅ Wrote story_gesture_overlay.py to {target}')\n"
        "    except Exception as e:\n"
        "        print(f'⚠️ Failed to write story_gesture_overlay.py: {e}')\n\n"
        "_ensure_story_gesture_overlay_module()\n\n"
        "# Import from working dir (preferred)\n"
        "sys.path.insert(0, '/kaggle/working')\n"
        "from poster_overlay import apply_poster_overlay\n"
        "from story_publish import preflight_story_publish_from_kaggle, publish_story_from_kaggle\n"
        "from story_gesture_overlay import GESTURE_STEP_COUNT, apply_story_gesture_frame\n"
    )
    sequence_init_old = (
        "    sequence = []\n"
        "    \n"
        "    for seg in segments:\n"
    )
    sequence_init_new = (
        "    sequence = []\n"
        "    gesture_step_index = 0\n"
        "    pending_gesture_step = None\n"
        "    pending_gesture_total = 0\n"
        "    pending_gesture_offset = 0\n"
        "    \n"
        "    for seg_index, seg in enumerate(segments):\n"
    )
    unfold_old = (
        "        # Unfold (Ball -> Flat)\n"
        "        if seg.unfold_len > 0:\n"
        "            unfold = render_motion(frames, seg.unfold_len, seg.easing_unfold, False, True)\n"
        "            sequence.extend(unfold)\n"
    )
    unfold_new = (
        "        # Unfold (Ball -> Flat)\n"
        "        if seg.unfold_len > 0:\n"
        "            unfold = render_motion(frames, seg.unfold_len, seg.easing_unfold, False, True)\n"
        "            if pending_gesture_step is not None and pending_gesture_total > 0:\n"
        "                unfold = [\n"
        "                    apply_story_gesture_frame(\n"
        "                        frame,\n"
        "                        step_index=pending_gesture_step,\n"
        "                        frame_index=pending_gesture_offset + idx,\n"
        "                        total_frames=pending_gesture_total,\n"
        "                        search_roots=OVERLAY_FONT_ROOTS,\n"
        "                    )\n"
        "                    for idx, frame in enumerate(unfold)\n"
        "                ]\n"
        "                pending_gesture_step = None\n"
        "                pending_gesture_total = 0\n"
        "                pending_gesture_offset = 0\n"
        "            sequence.extend(unfold)\n"
    )
    hold_ball_old = (
        "        # Hold Ball\n"
        "        for _ in range(seg.hold_ball):\n"
        "            sequence.append(ball)\n"
    )
    hold_ball_new = (
        "        # Hold Ball\n"
        "        ball_frames = [ball for _ in range(seg.hold_ball)]\n"
        "        next_unfold_len = 0\n"
        "        if seg_index + 1 < len(segments):\n"
        "            next_unfold_len = int(max(0, segments[seg_index + 1].unfold_len))\n"
        "        if gesture_step_index < GESTURE_STEP_COUNT and next_unfold_len > 0 and ball_frames:\n"
        "            interstitial_total = len(ball_frames) + next_unfold_len\n"
        "            ball_frames = [\n"
        "                apply_story_gesture_frame(\n"
        "                    frame,\n"
        "                    step_index=gesture_step_index,\n"
        "                    frame_index=idx,\n"
        "                    total_frames=interstitial_total,\n"
        "                    search_roots=OVERLAY_FONT_ROOTS,\n"
        "                )\n"
        "                for idx, frame in enumerate(ball_frames)\n"
        "            ]\n"
        "            pending_gesture_step = gesture_step_index\n"
        "            pending_gesture_total = interstitial_total\n"
        "            pending_gesture_offset = len(ball_frames)\n"
        "            gesture_step_index += 1\n"
        "        sequence.extend(ball_frames)\n"
    )
    telegram_cache_helper_old = (
        "def _prepare_telegram_cache(urls, posters_dir):\n"
        "    if not TELEGRAM_READY or not urls:\n"
        "        return {}\n"
        "    filenames_map = {}\n"
        "    url_map = {}\n"
        "    for idx, url in enumerate(urls):\n"
        "        if not isinstance(url, str):\n"
        "            continue\n"
        "        fname = url.split('/')[-1].split('?')[0]\n"
        "        if not fname:\n"
        "            continue\n"
        "        local_path = posters_dir / f\"tg_{idx}_{fname}\"\n"
        "        filenames_map[fname] = str(local_path)\n"
        "        url_map[url] = local_path\n"
        "    if filenames_map:\n"
        "        _run_async(download_via_telegram(filenames_map))\n"
        "    cache = {}\n"
        "    for url, path in url_map.items():\n"
        "        if path.exists():\n"
        "            cache[url] = path\n"
        "    if cache:\n"
        "        log(f\"✅ Telegram cache hits: {len(cache)}\")\n"
        "    return cache\n"
    )
    telegram_cache_helper_new = (
        "def _safe_telegram_cache_path(url: str, idx: int, posters_dir: Path) -> Path:\n"
        "    fname = str(url).split('/')[-1].split('?')[0]\n"
        "    suffix = Path(fname).suffix.lower()\n"
        "    if suffix not in {'.jpg', '.jpeg', '.png', '.webp'}:\n"
        "        suffix = '.jpg'\n"
        "    digest = hashlib.sha1(str(url).encode('utf-8')).hexdigest()[:16]\n"
        "    return posters_dir / f\"tg_{idx}_{digest}{suffix}\"\n"
        "\n"
        "\n"
        "def _prepare_telegram_cache(urls, posters_dir):\n"
        "    if not TELEGRAM_READY or not urls:\n"
        "        return {}\n"
        "    filenames_map = {}\n"
        "    url_map = {}\n"
        "    for idx, url in enumerate(urls):\n"
        "        if not isinstance(url, str):\n"
        "            continue\n"
        "        fname = url.split('/')[-1].split('?')[0]\n"
        "        if not fname:\n"
        "            continue\n"
        "        local_path = _safe_telegram_cache_path(url, idx, posters_dir)\n"
        "        filenames_map[fname] = str(local_path)\n"
        "        url_map[url] = local_path\n"
        "    if filenames_map:\n"
        "        _run_async(download_via_telegram(filenames_map))\n"
        "    cache = {}\n"
        "    for url, path in url_map.items():\n"
        "        try:\n"
        "            if path.exists():\n"
        "                cache[url] = path\n"
        "        except OSError:\n"
        "            continue\n"
        "    if cache:\n"
        "        log(f\"✅ Telegram cache hits: {len(cache)}\")\n"
        "    return cache\n"
    )
    telegram_cache_block_old = (
        "    if urls_to_cache:\n"
        "        filenames_map = {}\n"
        "        for idx, url in enumerate(urls_to_cache):\n"
        "            fname = url.split('/')[-1].split('?')[0]\n"
        "            if not fname:\n"
        "                continue\n"
        "            local_path = posters_dir / f\"tg_{idx}_{fname}\"\n"
        "            filenames_map[fname] = str(local_path)\n"
        "            url_map[url] = local_path\n"
        "        if TELEGRAM_READY and filenames_map:\n"
        "            _run_async(download_via_telegram(filenames_map))\n"
        "        elif not TELEGRAM_READY:\n"
        "            log(f\"[SKIP] Telegram cache disabled: {TELEGRAM_ERROR}\")\n"
        "        telegram_cache = {url: path for url, path in url_map.items() if path.exists()}\n"
        "        if telegram_cache:\n"
        "            log(f\"✅ Telegram cache hits: {len(telegram_cache)}\")\n"
    )
    telegram_cache_block_new = (
        "    if urls_to_cache:\n"
        "        telegram_cache = _prepare_telegram_cache(urls_to_cache, posters_dir)\n"
        "        if telegram_cache:\n"
        "            url_map.update(telegram_cache)\n"
    )

    replaced = False
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        raw_source = cell.get("source", "")
        source_was_list = isinstance(raw_source, list)
        source = "".join(raw_source) if source_was_list else str(raw_source)
        if "def _ensure_poster_overlay_module():" not in source:
            continue
        source = _replace_embedded_module(
            source,
            anchor="def _ensure_poster_overlay_module():",
            module_source=poster_module_source,
        )
        source = _replace_embedded_module(
            source,
            anchor="def _ensure_story_publish_module():",
            module_source=story_module_source,
        )
        if "def _ensure_story_gesture_overlay_module():" in source:
            source = _replace_embedded_module(
                source,
                anchor="def _ensure_story_gesture_overlay_module():",
                module_source=gesture_module_source,
            )
        elif helper_insert_old in source:
            source = source.replace(helper_insert_old, helper_insert_new, 1)
        else:
            raise RuntimeError("Could not locate story gesture helper insertion point in notebook")
        if overlay_call_old in source:
            source = source.replace(overlay_call_old, overlay_call_new, 1)
        elif overlay_call_new not in source:
            raise RuntimeError("Could not locate overlay call block in notebook")
        if sequence_init_old in source:
            source = source.replace(sequence_init_old, sequence_init_new, 1)
        elif sequence_init_new not in source:
            raise RuntimeError("Could not locate sequence init block in notebook")
        if unfold_old in source:
            source = source.replace(unfold_old, unfold_new, 1)
        elif unfold_new not in source:
            raise RuntimeError("Could not locate unfold block in notebook")
        if hold_ball_old in source:
            source = source.replace(hold_ball_old, hold_ball_new, 1)
        elif hold_ball_new not in source:
            raise RuntimeError("Could not locate hold-ball block in notebook")
        if telegram_cache_helper_old in source:
            source = source.replace(telegram_cache_helper_old, telegram_cache_helper_new, 1)
        elif telegram_cache_helper_new not in source:
            raise RuntimeError("Could not locate telegram cache helper block in notebook")
        if telegram_cache_block_old in source:
            source = source.replace(telegram_cache_block_old, telegram_cache_block_new, 1)
        elif telegram_cache_block_new not in source:
            raise RuntimeError("Could not locate telegram cache block in notebook")
        cell["source"] = source.splitlines(keepends=True) if source_was_list else source
        replaced = True
        break

    if not replaced:
        raise RuntimeError("Could not find CrumpleVideo pipeline cell in notebook")

    NOTEBOOK_PATH.write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
