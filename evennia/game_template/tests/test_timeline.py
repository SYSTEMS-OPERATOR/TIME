"""Unit tests for timeline helper utilities."""

from __future__ import annotations

import unittest

from evennia.game_template.world.timeline import (
    TimelineAnchor,
    generate_monthly_anchors,
    iso_z_from_utc,
    parse_utc_room_key,
    utc_room_key,
    validate_chronological_keys,
)


class TimelineHelpersTests(unittest.TestCase):
    """Validate canonical key generation and anchor creation."""

    def test_utc_room_key_roundtrip(self):
        key = utc_room_key(1123200)

        self.assertEqual(key, "UTC:1123200")
        self.assertEqual(parse_utc_room_key(key), 1123200)

    def test_parse_rejects_invalid_keys(self):
        with self.assertRaises(ValueError):
            parse_utc_room_key("1123200")
        with self.assertRaises(ValueError):
            parse_utc_room_key("UTC:")

    def test_iso_format(self):
        self.assertEqual(iso_z_from_utc(0), "1970-01-01T00:00:00Z")

    def test_anchor_generation_default_count(self):
        anchors = generate_monthly_anchors()

        self.assertEqual(len(anchors), 1200)
        self.assertIsInstance(anchors[0], TimelineAnchor)
        self.assertEqual(anchors[0].key, "UTC:0")
        self.assertEqual(anchors[-1].iso_alias, "2069-12-01T00:00:00Z")

    def test_validate_chronological_keys(self):
        ordered = ["UTC:0", "UTC:60", "UTC:120"]
        unordered = ["UTC:120", "UTC:0", "UTC:60"]

        self.assertTrue(validate_chronological_keys(ordered))
        self.assertFalse(validate_chronological_keys(unordered))


if __name__ == "__main__":
    unittest.main()
