"""Script typeclass with a practical template baseline."""

from evennia.scripts.scripts import DefaultScript


class Script(DefaultScript):
    """Base persistent script for game-level systems."""

    def at_script_creation(self):
        """Provide safe defaults for reusable template scripts."""
        super().at_script_creation()
        self.desc = self.desc or "Tracks a reusable TIME-EVE game system."
        self.persistent = True
