"""
At_initial_setup module template

Custom at_initial_setup method. This allows you to hook special
modifications to the initial server startup process. Note that this
will only be run once - when the server starts up for the very first
time! It is called last in the startup process and can thus be used to
overload things that happened before it.

The module must contain a global function at_initial_setup().  This
will be called without arguments. Note that tracebacks in this module
will be QUIETLY ignored, so make sure to check it well to make sure it
does what you expect it to.

"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

LOGGER = logging.getLogger(__name__)


def at_initial_setup():
    """Log first-run setup execution for easier boot diagnostics."""
    # Dev Agent Breadcrumb: first-time initialization entrypoint.
    LOGGER.info(
        "[Dev Agent Breadcrumb] initial_setup_ran utc=%s",
        datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
    )
