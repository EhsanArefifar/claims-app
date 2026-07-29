import logging
import os
import structlog


def configure_logging() -> None:
    """
    Configure structlog for the application.

    Renderer is chosen from the LOG_FORMAT env var (default: "json"):
    - "json"    → JSONRenderer: one compact JSON object per line.
                  Use in production / CI so logs are machine-parseable.
    - "console" → ConsoleRenderer: colorized, human-aligned output.
                  Set LOG_FORMAT=console locally for readable terminal output.

    Shared processors (run before the renderer in both modes):
    - merge_contextvars : merges context bound via structlog.contextvars
                          (the middleware binds request_id, method, path here)
    - add_log_level     : adds the "level" key (info, warning, error…)
    - TimeStamper       : adds "timestamp" in ISO-8601 UTC
    - StackInfoRenderer : renders stack_info if present
    - format_exc_info   : renders exception tracebacks into the event
    """

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    log_format = os.getenv("LOG_FORMAT", "json").lower()
    if log_format == "console":
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    # Configure stdlib logging independently of structlog.
    # structlog uses PrintLoggerFactory (calls print() directly) and never
    # touches stdlib at all.  basicConfig() only affects stdlib loggers such
    # as uvicorn's access log or SQLAlchemy's query log — setting the format
    # to "%(message)s" strips uvicorn's default prefix but leaves its lines
    # as plain text, NOT routed through the JSON pipeline above.
    # Net result: app logs → one-line JSON, uvicorn logs → plain text,
    # both in the same terminal.
    # Real integration (ProcessorFormatter on stdlib handlers) is a follow-up.
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
