from __future__ import annotations

import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


_DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def _env_enabled(name: str, *, default: bool = False) -> bool:
    raw = (os.getenv(name) or "").strip().lower()
    if not raw:
        return bool(default)
    return raw in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return int(default)
    try:
        return int(raw)
    except Exception:
        return int(default)


def _cleanup_old_runtime_logs(base_path: Path, *, retention_hours: int) -> None:
    cutoff_ts = time.time() - max(1, int(retention_hours)) * 3600
    prefix = f"{base_path.name}."
    for candidate in base_path.parent.iterdir():
        try:
            if not candidate.is_file():
                continue
            if candidate == base_path:
                continue
            if not candidate.name.startswith(prefix):
                continue
            if candidate.stat().st_mtime < cutoff_ts:
                candidate.unlink(missing_ok=True)
        except Exception:
            # Logging setup must stay best-effort; cleanup failures should not block startup.
            continue


def install_runtime_file_logging(logger: logging.Logger | None = None) -> logging.Handler | None:
    if not _env_enabled("ENABLE_RUNTIME_FILE_LOGGING", default=False):
        return None

    target_logger = logger or logging.getLogger()
    log_dir = Path((os.getenv("RUNTIME_LOG_DIR") or "/data/runtime_logs").strip() or "/data/runtime_logs")
    log_name = (os.getenv("RUNTIME_LOG_BASENAME") or "events-bot.log").strip() or "events-bot.log"
    retention_hours = max(1, _env_int("RUNTIME_LOG_RETENTION_HOURS", 24))
    backup_count = max(1, retention_hours - 1)
    log_level_name = (os.getenv("RUNTIME_LOG_LEVEL") or "").strip().upper()
    log_level = getattr(logging, log_level_name, target_logger.level or logging.INFO)

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        logging.getLogger(__name__).warning(
            "runtime_logging: failed to create log dir %s: %s",
            log_dir,
            exc,
        )
        return None

    log_path = log_dir / log_name
    resolved_log_path = str(log_path.resolve())
    for handler in target_logger.handlers:
        if getattr(handler, "_evbot_runtime_log_path", None) == resolved_log_path:
            return handler

    try:
        _cleanup_old_runtime_logs(log_path, retention_hours=retention_hours)
        handler = TimedRotatingFileHandler(
            filename=log_path,
            when="H",
            interval=1,
            backupCount=backup_count,
            encoding="utf-8",
            delay=True,
            utc=True,
        )
        handler.setLevel(log_level)
        handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
        handler._evbot_runtime_log_path = resolved_log_path  # type: ignore[attr-defined]
        target_logger.addHandler(handler)
        logging.getLogger(__name__).info(
            "runtime_logging: enabled path=%s retention_hours=%d backup_count=%d level=%s",
            resolved_log_path,
            retention_hours,
            backup_count,
            logging.getLevelName(log_level),
        )
        return handler
    except Exception as exc:
        logging.getLogger(__name__).warning(
            "runtime_logging: failed to init file handler path=%s error=%s",
            resolved_log_path,
            exc,
        )
        return None
