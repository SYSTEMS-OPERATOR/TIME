"""Shared command helpers for the game template."""

from evennia.commands.command import Command as BaseCommand


class Command(BaseCommand):
    """Base command with small debugging affordances for template projects."""

    def at_pre_cmd(self):
        """Capture the raw command line as a runtime breadcrumb when possible."""
        caller = getattr(self, "caller", None)
        remember = getattr(caller, "remember_breadcrumb", None)
        if callable(remember):
            remember(
                "command_invoked",
                command=getattr(self, "key", None),
                args=getattr(self, "args", ""),
            )
        return super().at_pre_cmd()
