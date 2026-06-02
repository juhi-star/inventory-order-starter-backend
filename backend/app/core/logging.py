from __future__ import annotations

import logging
import sys
from typing import cast

import structlog
from structlog.stdlib import BoundLogger
from structlog.types import EventDict, Processor


def _drop_color_message_key(_: object, __: str, event_dict: EventDict) -> EventDict:
    event_dict.pop("color_message", None)
    return event_dict


def configure_logging(level: str = "INFO") -> None:
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _drop_color_message_key,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[*shared_processors, structlog.processors.JSONRenderer()],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level.upper(), logging.INFO),
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    for noisy in ("uvicorn.access", "uvicorn.error"):
        logging.getLogger(noisy).handlers.clear()
        logging.getLogger(noisy).propagate = True


def get_logger(name: str | None = None) -> BoundLogger:
    return cast(BoundLogger, structlog.get_logger(name))
