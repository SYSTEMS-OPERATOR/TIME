"""Room typeclass with clearer builder-facing defaults."""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """Default room class used by the game template."""

    def at_object_creation(self):
        """Seed a room with a helpful description for unfinished areas."""
        super().at_object_creation()
        self.remember_breadcrumb("room_initialized", room=getattr(self, "key", None))
