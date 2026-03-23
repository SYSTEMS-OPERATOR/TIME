"""Account typeclasses with simple lifecycle breadcrumbs."""

from evennia.accounts.accounts import DefaultAccount, DefaultGuest


class Account(DefaultAccount):
    """Base account typeclass for the game template."""

    def remember_breadcrumb(self, event, **details):
        """Store lightweight account flow notes on ``ndb`` for debugging."""
        trail = list(getattr(self.ndb, "dev_breadcrumbs", []))
        trail.append({"event": event, "details": details})
        self.ndb.dev_breadcrumbs = trail[-20:]

    def at_account_creation(self):
        """Initialize persistent account defaults the template depends on."""
        super().at_account_creation()
        if getattr(self.db, "profile_tagline", None) is None:
            self.db.profile_tagline = "A newly awakened explorer of TIME-EVE."
        self.remember_breadcrumb("account_created", account=getattr(self, "key", None))

    def at_post_login(self, session=None, **kwargs):
        """Record successful logins for local debugging."""
        super().at_post_login(session=session, **kwargs)
        self.remember_breadcrumb(
            "account_login",
            session=getattr(session, "sessid", None),
        )

    def at_disconnect(self, reason=None, **kwargs):
        """Record disconnections for local debugging."""
        super().at_disconnect(reason=reason, **kwargs)
        self.remember_breadcrumb("account_disconnect", reason=reason)


class Guest(DefaultGuest):
    """Guest accounts inherit Evennia defaults unchanged."""
