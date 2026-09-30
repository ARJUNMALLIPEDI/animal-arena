from __future__ import annotations

import logging
import sys

from .config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    root = logging.getLogger()
    if root.handlers:
        # Already configured (e.g. under a test runner or reload) -- avoid
        # duplicate handlers.
        root.setLevel(settings.log_level)
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s :: %(message)s")
    )
    root.addHandler(handler)
    root.setLevel(settings.log_level)

    # Keep third-party libraries quieter than our own app logs by default.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
