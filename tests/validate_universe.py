#!/usr/bin/env python3
"""Static graph and updater regression checks, with no external requests."""
import copy
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("update_universe", ROOT / "tools/update_universe.py")
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class UniverseTests(unittest.TestCase):
    def setUp(self):
        self.texts = {name: (ROOT / name).read_text() for name in updater.PAGES}
        self.graph = updater.read_graph(self.texts["index.html"])

    def test_graph_schema_references_and_uniqueness(self):
        updater.validate_graph(self.graph)

    def test_home_and_universe_are_synchronized(self):
        self.assertEqual(self.graph, updater.read_graph(self.texts["universe/index.html"]))

    def test_mobile_capacity_and_documented_counts(self):
        for text in self.texts.values():
            self.assertLessEqual(len(self.graph["concepts"]), int(re.search(r"mobileNodes:(\d+)", text)[1]))
        readme = (ROOT / "README.md").read_text()
        self.assertIn(f"{len(self.graph['concepts'])} have public concept labels", readme)
        self.assertIn(f"the {len(self.graph['paths'])} relationships from `#path-data`", readme)

    def test_public_graph_uses_capabilities_not_named_partners(self):
        for text in (str(self.graph["concepts"]), str(self.graph["paths"])):
            for name in ("GetJacked", "Get Jacked", "Ticket Rewards", "Outlandish", "Astra Media", "Ampley", "Dubble"):
                self.assertNotIn(name.casefold(), text.casefold())

    def test_existing_loyalty_path_is_preserved_once(self):
        expected = ["Live entertainment", "Promotions & incentives", "Loyalty", "Customer retention"]
        self.assertEqual(sum(path["nodes"] == expected for path in self.graph["paths"]), 1)

    def test_home_belief_link_has_a_real_target(self):
        self.assertIn('id="read-universe" href="/universe/#universe-guide"', self.texts["index.html"])
        self.assertIn('id="universe-guide"', self.texts["universe/index.html"])

    def test_reapplying_the_same_additions_is_idempotent(self):
        self.assertEqual(self.graph, updater.merge_additions(self.graph, copy.deepcopy(self.graph)))

    def test_conflicting_concept_is_rejected(self):
        concept = dict(self.graph["concepts"][0], description="A conflicting edit")
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            updater.merge_additions(self.graph, {"concepts": [concept], "paths": []})

    def test_invalid_path_reference_is_rejected(self):
        bad = copy.deepcopy(self.graph)
        bad["paths"][0]["nodes"][0] = "Missing concept"
        with self.assertRaisesRegex(ValueError, "Unknown concepts"):
            updater.validate_graph(bad)

    def test_duplicate_and_invalid_fields_are_rejected(self):
        bad = copy.deepcopy(self.graph)
        bad["concepts"].append(dict(bad["concepts"][0], name=bad["concepts"][0]["name"].upper()))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            updater.validate_graph(bad)
        bad = copy.deepcopy(self.graph)
        bad["concepts"][0]["group"] = "unknown"
        with self.assertRaisesRegex(ValueError, "group/kind"):
            updater.validate_graph(bad)

    def test_new_concept_without_a_path_is_rejected(self):
        concept = dict(self.graph["concepts"][0], name="Unconnected capability")
        with self.assertRaisesRegex(ValueError, "need a pathway"):
            updater.merge_additions(self.graph, {"concepts": [concept], "paths": []})

    def test_markup_is_rejected(self):
        bad = copy.deepcopy(self.graph)
        bad["concepts"][0]["description"] = "</script><script>alert(1)</script>"
        with self.assertRaisesRegex(ValueError, "plain text"):
            updater.validate_graph(bad)

    def test_failed_write_restores_all_original_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            originals = {"home.html": "old home", "universe.html": "old universe", "README.md": "old counts"}
            for name, text in originals.items():
                (root / name).write_text(text)
            replace = updater.os.replace
            calls = 0

            def fail_second_replace(source, destination):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("Injected write failure")
                replace(source, destination)

            with patch.object(updater, "ROOT", root), patch.object(updater.os, "replace", fail_second_replace):
                with self.assertRaisesRegex(OSError, "all replaced files were restored"):
                    updater.write_changes({name: "new content" for name in originals})
            for name, text in originals.items():
                self.assertEqual((root / name).read_text(), text)
            self.assertEqual(sorted(path.name for path in root.iterdir()), sorted(originals))

    def test_successful_write_updates_every_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            changes = {"home.html": "new home", "universe.html": "new universe", "README.md": "new counts"}
            for name in changes:
                (root / name).write_text("old content")
            with patch.object(updater, "ROOT", root):
                updater.write_changes(changes)
                updater.write_changes(changes)
            for name, text in changes.items():
                self.assertEqual((root / name).read_text(), text)
            self.assertEqual(sorted(path.name for path in root.iterdir()), sorted(changes))


if __name__ == "__main__":
    unittest.main(verbosity=2)
