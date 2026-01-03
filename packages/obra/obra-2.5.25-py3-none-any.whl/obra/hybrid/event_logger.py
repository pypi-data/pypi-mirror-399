"""Minimal event logger for hybrid mode observability (ISSUE-SAAS-042).

This module provides a standalone event logger that works in both:
- Development environment (running from source)
- Installed package (pip install obra)

The logger writes JSONL events to ~/obra-runtime/logs/hybrid.jsonl.

Why this exists:
- ProductionLogger (src/monitoring/production_logger.py) is not packaged
- Sessions run from installed package had no event logging (silent failure)
- This minimal implementation provides observability for all obra users

Design principles:
- No dependencies on src/ modules (must work in installed package)
- Thread-safe for concurrent event logging
- Simple JSONL format compatible with ProductionLogger events
- Immediate flush for real-time monitoring
"""

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)


class HybridEventLogger:
    """Minimal JSONL event logger for hybrid mode.

    Thread-safe event logger that writes structured events to a JSONL file.
    Compatible with ProductionLogger event format for tooling compatibility.

    Example:
        >>> logger = HybridEventLogger()
        >>> logger.log_event("session_started", session_id="abc-123", objective="test")
    """

    def __init__(self, log_path: Path | None = None):
        """Initialize HybridEventLogger.

        Args:
            log_path: Path to log file. Defaults to ~/obra-runtime/logs/hybrid.jsonl
        """
        self._lock = Lock()
        self._log_path = log_path or self._get_default_log_path()

        # Ensure log directory exists
        self._log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(f"HybridEventLogger initialized: {self._log_path}")

    @staticmethod
    def _get_default_log_path() -> Path:
        """Get the default log file path.

        Returns:
            Path to ~/obra-runtime/logs/hybrid.jsonl
        """
        runtime_dir = Path(os.environ.get("OBRA_RUNTIME_DIR", "~/obra-runtime")).expanduser()
        return runtime_dir / "logs" / "hybrid.jsonl"

    def log_event(self, event_type: str, session_id: str = "", **kwargs: Any) -> None:
        """Log a structured event to the JSONL file.

        Args:
            event_type: Type of event (session_started, phase_started, etc.)
            session_id: Session ID for event correlation
            **kwargs: Event-specific data

        Example:
            >>> logger.log_event(
            ...     "derivation_started",
            ...     session_id="abc-123",
            ...     objective="Build calculator app"
            ... )
        """
        with self._lock:
            try:
                now_iso = datetime.now(UTC).isoformat()
                event = {
                    "type": event_type,
                    "ts": now_iso,
                    "timestamp": now_iso,
                    "session": session_id,
                    **kwargs,
                }

                # Append JSONL line to file
                with open(self._log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(event, default=str) + "\n")
                    f.flush()  # Immediate flush for real-time monitoring

            except Exception as e:
                # Never fail the main operation due to logging
                logger.warning(f"Failed to log event '{event_type}': {e}")


# Module-level singleton for convenience
_hybrid_logger: HybridEventLogger | None = None


def get_hybrid_logger() -> HybridEventLogger:
    """Get or create the module-level HybridEventLogger instance.

    Returns:
        HybridEventLogger singleton instance
    """
    global _hybrid_logger
    if _hybrid_logger is None:
        _hybrid_logger = HybridEventLogger()
    return _hybrid_logger


__all__ = ["HybridEventLogger", "get_hybrid_logger"]
