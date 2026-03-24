"""Core object typeclasses for the game template.

Dev Agent Breadcrumbs:
    The helpers in :class:`ObjectParent` record lightweight runtime notes in
    ``self.ndb.dev_breadcrumbs`` so builders and developers can inspect the
    recent logic flow while iterating on a new game.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from evennia.objects.objects import DefaultObject

_DEFAULT_OBJECT_DESC = "You see nothing special."
_DEFAULT_ROOM_DESC = (
    "An unfinished room waits here for a builder to describe it."
)
_BREADCRUMB_LIMIT = 20


class ObjectParent:
    """Shared helpers for all in-world entities.

    The mixin focuses on safe, template-friendly behavior:

    * sensible default descriptions for unfinished content
    * lightweight Dev Agent Breadcrumbs for debugging logic flow
    * small utility hooks that are safe to inherit everywhere
    """

    def remember_breadcrumb(
        self, event: str, **details: Any
    ) -> dict[str, Any]:
        """Store a short runtime breadcrumb on the non-persistent handler.

        Args:
            event: Short event name describing what happened.
            **details: Optional serializable details to help debugging.

        Returns:
            The breadcrumb entry that was stored.
        """
        ndb = getattr(self, "ndb", None)
        if ndb is None:
            return {
                "timestamp": datetime.now(tz=timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "event": event,
                "details": details,
            }

        trail_raw = getattr(ndb, "dev_breadcrumbs", None)
        trail = list(trail_raw) if isinstance(trail_raw, (list, tuple)) else []
        entry = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(
                timespec="seconds"
            ),
            "event": event,
            "details": details,
        }
        trail.append(entry)
        ndb.dev_breadcrumbs = trail[-_BREADCRUMB_LIMIT:]
        return entry

    def get_breadcrumbs(self) -> list[dict[str, Any]]:
        """Return the current runtime breadcrumb trail."""
        return list(getattr(self.ndb, "dev_breadcrumbs", []))

    def clear_breadcrumbs(self) -> None:
        """Clear the stored runtime breadcrumbs."""
        self.ndb.dev_breadcrumbs = []

    def get_default_desc(self) -> str:
        """Return a fallback description suitable for the object's role."""
        is_room = (
            getattr(self, "location", None) is None
            and hasattr(self, "exits")
        )
        return _DEFAULT_ROOM_DESC if is_room else _DEFAULT_OBJECT_DESC

    def ensure_default_desc(self) -> str:
        """Populate ``db.desc`` if the object does not yet define one."""
        desc = getattr(self.db, "desc", None)
        if not desc:
            desc = self.get_default_desc()
            self.db.desc = desc
        return desc

    def at_object_creation(self) -> None:
        """Initialize template defaults when the object is first created."""
        super().at_object_creation()
        self.ensure_default_desc()
        self.remember_breadcrumb(
            "object_created",
            key=getattr(self, "key", "unknown"),
            typeclass=self.__class__.__name__,
        )

    def get_display_desc(self, looker, **kwargs):
        """Return a useful description even for unfinished template objects."""
        self.remember_breadcrumb(
            "display_desc_requested",
            looker=getattr(looker, "key", None),
        )
        desc = super().get_display_desc(looker, **kwargs)
        return desc or self.ensure_default_desc()

    def at_post_move(self, source_location, move_type="move", **kwargs):
        """Record movement for debugging while preserving default behavior."""
        super().at_post_move(source_location, move_type=move_type, **kwargs)
        self.remember_breadcrumb(
            "post_move",
            source=getattr(source_location, "key", None),
            destination=getattr(getattr(self, "location", None), "key", None),
            move_type=move_type,
        )


class Object(ObjectParent, DefaultObject):
    """Base in-world object for the game template."""
