"""Tests for the TIME-EVE game template helpers.

The real Evennia runtime depends on Django and a configured game environment.
These tests stub the narrow import surface needed to validate the template logic
in isolation.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]


class _DefaultBase:
    """Small stand-in for Evennia default classes used in tests."""

    def at_object_creation(self):
        return None

    def get_display_desc(self, looker, **kwargs):
        return getattr(getattr(self, "db", None), "desc", None)

    def at_post_move(self, source_location, move_type="move", **kwargs):
        return None

    def at_account_creation(self):
        return None

    def at_post_login(self, session=None, **kwargs):
        return None

    def at_disconnect(self, reason=None, **kwargs):
        return None

    def format_message(self, msg, emit=False):
        return msg

    def at_script_creation(self):
        return None

    def at_pre_cmd(self):
        return None

    def at_traverse(self, traversing_object, target_location, **kwargs):
        return target_location


class TemplateModuleLoader:
    """Helper for loading template modules with stubbed dependencies."""

    @staticmethod
    def install_evennia_stubs():
        """Install a minimal fake Evennia module tree into ``sys.modules``."""
        stubs = {
            "evennia": ModuleType("evennia"),
            "evennia.objects": ModuleType("evennia.objects"),
            "evennia.objects.objects": ModuleType("evennia.objects.objects"),
            "evennia.accounts": ModuleType("evennia.accounts"),
            "evennia.accounts.accounts": ModuleType("evennia.accounts.accounts"),
            "evennia.comms": ModuleType("evennia.comms"),
            "evennia.comms.comms": ModuleType("evennia.comms.comms"),
            "evennia.scripts": ModuleType("evennia.scripts"),
            "evennia.scripts.scripts": ModuleType("evennia.scripts.scripts"),
            "evennia.commands": ModuleType("evennia.commands"),
            "evennia.commands.command": ModuleType("evennia.commands.command"),
            "evennia.game_template": ModuleType("evennia.game_template"),
            "evennia.game_template.typeclasses": ModuleType(
                "evennia.game_template.typeclasses"
            ),
            "evennia.game_template.commands": ModuleType("evennia.game_template.commands"),
        }
        stubs["evennia.objects.objects"].DefaultObject = _DefaultBase
        stubs["evennia.objects.objects"].DefaultCharacter = _DefaultBase
        stubs["evennia.objects.objects"].DefaultRoom = _DefaultBase
        stubs["evennia.objects.objects"].DefaultExit = _DefaultBase
        stubs["evennia.accounts.accounts"].DefaultAccount = _DefaultBase
        stubs["evennia.accounts.accounts"].DefaultGuest = _DefaultBase
        stubs["evennia.comms.comms"].DefaultChannel = _DefaultBase
        stubs["evennia.scripts.scripts"].DefaultScript = _DefaultBase
        stubs["evennia.commands.command"].Command = _DefaultBase
        for name, module in stubs.items():
            sys.modules[name] = module

    @staticmethod
    def load_module(module_name, relative_path):
        """Load a project module directly from disk under ``module_name``."""
        spec = spec_from_file_location(module_name, ROOT / relative_path)
        module = module_from_spec(spec)
        sys.modules[module_name] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module


TemplateModuleLoader.install_evennia_stubs()
OBJECTS = TemplateModuleLoader.load_module(
    "evennia.game_template.typeclasses.objects",
    "evennia/game_template/typeclasses/objects.py",
)
ACCOUNTS = TemplateModuleLoader.load_module(
    "evennia.game_template.typeclasses.accounts",
    "evennia/game_template/typeclasses/accounts.py",
)
CHANNELS = TemplateModuleLoader.load_module(
    "evennia.game_template.typeclasses.channels",
    "evennia/game_template/typeclasses/channels.py",
)
COMMANDS = TemplateModuleLoader.load_module(
    "evennia.game_template.commands.command",
    "evennia/game_template/commands/command.py",
)


class DummyParent(OBJECTS.ObjectParent):
    """Minimal stand-in exposing the mixin logic without the DB layer."""

    def __init__(self, desc=None, location="somewhere", exits=None):
        self.db = SimpleNamespace(desc=desc)
        self.ndb = SimpleNamespace(dev_breadcrumbs=[])
        self.location = location
        self.exits = exits if exits is not None else []
        self.key = "Dummy"


class ObjectParentTests(unittest.TestCase):
    """Verify the template object helpers work in isolation."""

    def test_ensure_default_desc_sets_object_fallback(self):
        dummy = DummyParent(desc=None, location="inventory")

        desc = dummy.ensure_default_desc()

        self.assertEqual(desc, OBJECTS._DEFAULT_OBJECT_DESC)
        self.assertEqual(dummy.db.desc, OBJECTS._DEFAULT_OBJECT_DESC)

    def test_ensure_default_desc_sets_room_fallback(self):
        dummy = DummyParent(desc=None, location=None, exits=[])

        desc = dummy.ensure_default_desc()

        self.assertEqual(desc, OBJECTS._DEFAULT_ROOM_DESC)

    def test_remember_breadcrumb_caps_history(self):
        dummy = DummyParent()

        for index in range(25):
            dummy.remember_breadcrumb("step", index=index)

        self.assertEqual(len(dummy.get_breadcrumbs()), 20)
        self.assertEqual(dummy.get_breadcrumbs()[0]["details"]["index"], 5)


class AccountTests(unittest.TestCase):
    """Verify account defaults without the full Evennia runtime."""

    def test_account_creation_sets_profile_tagline(self):
        account = object.__new__(ACCOUNTS.Account)
        account.db = SimpleNamespace(profile_tagline=None)
        account.ndb = SimpleNamespace(dev_breadcrumbs=[])
        account.key = "Tester"

        with patch.object(_DefaultBase, "at_account_creation", return_value=None) as mocked_super:
            ACCOUNTS.Account.at_account_creation(account)

        mocked_super.assert_called_once_with()
        self.assertEqual(
            account.db.profile_tagline,
            "A newly awakened explorer of TIME-EVE.",
        )
        self.assertEqual(account.ndb.dev_breadcrumbs[-1]["event"], "account_created")


class ChannelTests(unittest.TestCase):
    """Verify the channel formatting fallback."""

    def test_blank_messages_collapse_to_ellipsis(self):
        channel = object.__new__(CHANNELS.Channel)

        with patch.object(_DefaultBase, "format_message", return_value="   "):
            self.assertEqual(CHANNELS.Channel.format_message(channel, msg="ignored"), "...")


class CommandTests(unittest.TestCase):
    """Verify the command breadcrumb helper."""

    def test_pre_cmd_records_breadcrumb_when_available(self):
        breadcrumbs = []

        def remember(event, **details):
            breadcrumbs.append((event, details))

        command = object.__new__(COMMANDS.Command)
        command.caller = SimpleNamespace(remember_breadcrumb=remember)
        command.key = "look"
        command.args = "at room"

        with patch.object(_DefaultBase, "at_pre_cmd", return_value=None) as mocked_super:
            result = COMMANDS.Command.at_pre_cmd(command)

        self.assertIsNone(result)
        mocked_super.assert_called_once_with()
        self.assertEqual(
            breadcrumbs,
            [("command_invoked", {"command": "look", "args": "at room"})],
        )


if __name__ == "__main__":
    unittest.main()
