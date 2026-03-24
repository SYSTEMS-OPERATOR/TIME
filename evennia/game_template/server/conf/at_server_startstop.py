"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.

This module must contain at least these global functions:

at_server_init()
at_server_start()
at_server_stop()
at_server_reload_start()
at_server_reload_stop()
at_server_cold_start()
at_server_cold_stop()

"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

LOGGER = logging.getLogger(__name__)


def _log_hook(hook_name: str) -> None:
    """Log a consistent Dev Agent Breadcrumb for lifecycle visibility."""
    # Dev Agent Breadcrumb: Server lifecycle hook entrypoint.
    LOGGER.info(
        "[Dev Agent Breadcrumb] server_hook=%s utc=%s",
        hook_name,
        datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
    )


def at_server_init():
    """
    This is called first as the server is starting up, regardless of how.
    """
    _log_hook("at_server_init")


def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    _log_hook("at_server_start")


def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    _log_hook("at_server_stop")


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    _log_hook("at_server_reload_start")


def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    _log_hook("at_server_reload_stop")


def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    _log_hook("at_server_cold_start")


def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    _log_hook("at_server_cold_stop")
