"""Character typeclass with template-safe defaults and breadcrumbs."""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """Default playable character for the game template."""

    def at_post_puppet(self, **kwargs):
        """Record when an account starts controlling this character."""
        super().at_post_puppet(**kwargs)
        self.remember_breadcrumb(
            "character_puppeted",
            account=getattr(getattr(self, "account", None), "key", None),
        )

    def at_post_unpuppet(self, account, session=None, **kwargs):
        """Record when control of the character ends."""
        super().at_post_unpuppet(account, session=session, **kwargs)
        self.remember_breadcrumb(
            "character_unpuppeted",
            account=getattr(account, "key", None),
        )
