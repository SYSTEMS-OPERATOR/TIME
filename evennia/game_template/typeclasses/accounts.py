"""Account typeclasses with simple lifecycle breadcrumbs."""

from evennia.accounts.accounts import DefaultAccount, DefaultGuest


class Account(DefaultAccount):
    """Base account typeclass for the game template."""

    def remember_breadcrumb(self, event, **details):
        """Store lightweight account flow notes on ``ndb`` for debugging."""
        ndb = getattr(self, "ndb", None)
        if ndb is None:
            return None

        trail_raw = getattr(ndb, "dev_breadcrumbs", None)
        trail = list(trail_raw) if isinstance(trail_raw, (list, tuple)) else []
        trail.append({"event": event, "details": details})
        ndb.dev_breadcrumbs = trail[-20:]
        return trail[-1]

    def at_account_creation(self):
        """Initialize lightweight defaults the template depends on."""
        super().at_account_creation()
        # Dev Agent Breadcrumb:
        # Avoid persistent Attribute writes during first-save bootstrap. This
        # keeps account initialization safer across SQLite transactional paths.
        self.remember_breadcrumb(
            "account_created",
            account=getattr(self, "key", None),
        )

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
