#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from video_announce.kaggle_client import KaggleClient


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("cherryflash_intro_scene1")

TEMPLATE_KERNEL_DIR = PROJECT_ROOT / "kaggle" / "CherryFlash"
OUTPUT_DIR = PROJECT_ROOT / "artifacts" / "codex" / "cherryflash_kaggle_intro_scene1"
OUTPUT_FILE_NAME = "cherryflash_intro_scene1_final.mp4"


async def run_cherryflash_intro_scene1() -> bool:
    client = KaggleClient()
    if not TEMPLATE_KERNEL_DIR.exists():
        raise FileNotFoundError(
            f"CherryFlash kernel template directory missing: {TEMPLATE_KERNEL_DIR}"
        )

    meta = json.loads(
        (TEMPLATE_KERNEL_DIR / "kernel-metadata.json").read_text(encoding="utf-8")
    )
    kernel_ref = meta["id"]

    logger.info(
        "Pushing CherryFlash Kaggle notebook bootstrap from %s",
        TEMPLATE_KERNEL_DIR,
    )
    client.push_kernel(kernel_path=TEMPLATE_KERNEL_DIR)

    start = time.time()
    max_wait = 6 * 60 * 60
    while time.time() - start < max_wait:
        status_info = client.get_kernel_status(kernel_ref)
        status = str(status_info.get("status") or "").upper()
        logger.info("CherryFlash kernel status: %s", status)
        if status == "COMPLETE":
            break
        if status in {"ERROR", "FAILED", "CANCELLED"}:
            raise RuntimeError(f"CherryFlash kernel failed: {status_info}")
        await asyncio.sleep(30)
    else:
        raise TimeoutError("CherryFlash Kaggle render timed out")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = client.download_kernel_output(kernel_ref, path=OUTPUT_DIR, force=True)
    logger.info("Downloaded Kaggle output files: %s", files)

    matches = sorted(OUTPUT_DIR.rglob(OUTPUT_FILE_NAME))
    if not matches:
        raise FileNotFoundError(
            f"{OUTPUT_FILE_NAME} not found in downloaded Kaggle output"
        )
    logger.info("CherryFlash approval output ready: %s", matches[0])
    return True


if __name__ == "__main__":
    ok = asyncio.run(run_cherryflash_intro_scene1())
    raise SystemExit(0 if ok else 1)
