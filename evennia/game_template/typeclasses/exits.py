"""Exit typeclass with traversal breadcrumbs."""

from evennia.objects.objects import DefaultExit

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """Default exit class used by the game template."""

    def at_traverse(self, traversing_object, target_location, **kwargs):
        """Record traversal attempts while keeping the standard exit logic."""
        self.remember_breadcrumb(
            "exit_traversed",
            traveler=getattr(traversing_object, "key", None),
            destination=getattr(target_location, "key", None),
        )
        return super().at_traverse(traversing_object, target_location, **kwargs)
