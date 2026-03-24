"""
ServerSession

The serversession is the Server-side in-memory representation of a
user connecting to the game.  Evennia manages one Session per
connection to the game. So a user logged into the game with multiple
clients (if Evennia is configured to allow that) will have multiple
sessions tied to one Account object. All communication between Evennia
and the real-world user goes through the Session(s) associated with that user.

It should be noted that modifying the Session object is not usually
necessary except for the most custom and exotic designs - and even
then it might be enough to just add custom session-level commands to
the SessionCmdSet instead.

This module is not normally called. To tell Evennia to use the class
in this module instead of the default one, add the following to your
settings file:

    SERVER_SESSION_CLASS = "server.conf.serversession.ServerSession"

"""

from evennia.server.serversession import ServerSession as BaseServerSession


class ServerSession(BaseServerSession):
    """
    This class represents a player's session and is a template for
    individual protocols to communicate with Evennia.

    Each account gets one or more sessions assigned to them whenever they connect
    to the game server. All communication between game and account goes
    through their session(s).
    """

    def _remember_session_breadcrumb(self, event: str, **details):
        """Store non-persistent session breadcrumbs when possible."""
        ndb = getattr(self, "ndb", None)
        if ndb is None:
            return None

        trail = list(getattr(ndb, "dev_breadcrumbs", []))
        entry = {"event": event, "details": details}
        trail.append(entry)
        ndb.dev_breadcrumbs = trail[-20:]
        return entry

    def at_login(self):
        """Capture login transitions in Dev Agent Breadcrumbs."""
        self._remember_session_breadcrumb("session_login", sessid=getattr(self, "sessid", None))
        return super().at_login()

    def at_disconnect(self, reason=None):
        """Capture disconnect transitions in Dev Agent Breadcrumbs."""
        self._remember_session_breadcrumb(
            "session_disconnect",
            reason=str(reason) if reason else None,
        )
        return super().at_disconnect(reason=reason)
