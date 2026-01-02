"""Utility functions for TurnWise SDK."""
import logging


def setup_logging(level: int = logging.INFO) -> None:
    """
    Set up logging for the SDK.

    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Set SDK loggers
    logging.getLogger("turnwise").setLevel(level)


__all__ = ["setup_logging"]
