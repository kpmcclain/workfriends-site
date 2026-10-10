#!/usr/bin/env python3
"""Static regression checks for Workfriends' public reference and offer copy.

Run from any directory: python3 tests/validate_public_content.py
No build step or third-party packages are required.
"""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def normalized(text):
    return re.sub(r"\s+", " ", text).strip()


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.scripts = []
        self.current_script = None
        self.suppressed = 0
        self.canonicals = []
        self.robots = []
        self.feed((ROOT / path).read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("style", "script", "svg"):
            self.suppressed += 1
        if tag == "script":
            self.current_script = [attrs.get("type", ""), ""]
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))
        if tag == "meta" and attrs.get("name") == "robots":
            self.robots.append(attrs.get("content", ""))

    def handle_endtag(self, tag):
        if tag == "script" and self.current_script is not None:
            self.scripts.append(self.current_script)
            self.current_script = None
        if tag in ("style", "script", "svg"):
            self.suppressed -= 1

    def handle_data(self, data):
        if self.current_script is not None:
            self.current_script[1] += data
        elif not self.suppressed:
            self.text.append(data)

    @property
    def visible(self):
        return normalized(" ".join(self.text))

    @property
    def structured(self):
        return [json.loads(content) for kind, content in self.scripts
                if kind == "application/ld+json"]


class PublicContentTests(unittest.TestCase):
    def test_all_structured_data_is_valid_json(self):
        for path in ROOT.rglob("*.html"):
            with self.subTest(path=path.relative_to(ROOT)):
                page = Page(path.relative_to(ROOT))
                for data in page.structured:
                    self.assertEqual(data["@context"], "https://schema.org")
                if path.name == "404.html":
                    self.assertEqual(page.canonicals, [])
                else:
                    self.assertEqual(len(page.canonicals), 1)
                    self.assertTrue(page.canonicals[0].startswith("https://www.getworkfriends.co/"))

    def test_edited_faq_schema_matches_visible_answers(self):
        for path in ("creator-commerce/index.html", "for-ai.html"):
            page = Page(path)
            for data in page.structured:
                for node in data.get("@graph", []):
                    if node.get("@type") == "FAQPage":
                        for question in node["mainEntity"]:
                            with self.subTest(page=path, question=question["name"]):
                                self.assertIn(normalized(question["name"]), page.visible)
                                self.assertIn(normalized(question["acceptedAnswer"]["text"]), page.visible)

    def test_free_snapshot_and_paid_scope_are_distinct(self):
        for path in ("tiktok-shop/index.html", "creator-commerce/index.html", "for-ai.html"):
            text = Page(path).visible
            with self.subTest(path=path):
                self.assertIn("Market Opportunity Snapshot", text)
                self.assertIn("Gut Check", text)
                self.assertIn("initial view of category opportunity, key questions and possible next steps", text)
                self.assertNotIn("exact category gap", text)
        self.assertIn("agreed scope and fee before work begins", Page("tiktok-shop/index.html").visible)
        self.assertIn("scoped paid work", Page("creator-commerce/index.html").visible)

    def test_partner_references_preserve_approved_operating_partners(self):
        partners = ("Outlandish", "Astra Media", "Ampley", "Dubble", "Ticket Rewards", "Iconically")
        for path in ("network/index.html", "for-ai.html"):
            page = Page(path)
            for name in partners:
                with self.subTest(page=path, partner=name):
                    self.assertIn(name, page.visible)
        ai = Page("for-ai.html").visible
        self.assertIn("Get Live", ai)
        self.assertIn("not a requirement for every buyer or collaborator", ai)
        llms = (ROOT / "llms.txt").read_text()
        self.assertIn("Outlandish, Astra Media, Ampley, Dubble, Ticket Rewards and Iconically", llms)
        self.assertIn("Get Live", llms)

    def test_universe_reference_matches_the_simplified_page(self):
        ai = Page("for-ai.html").visible
        self.assertNotIn("167 concepts and 19 commercial pathways", ai)
        self.assertNotIn("readable map of roles, capabilities and outcomes", ai)
        self.assertIn("belief, explanation of the network and invitation to participate", ai)
        universe = Page("universe/index.html").visible
        self.assertIn("People outlast companies.", universe)
        self.assertIn("Find your place in the network", universe)

    def test_thanks_remains_noindex_and_outside_sitemap(self):
        self.assertTrue(any("noindex" in rule for rule in Page("thanks/index.html").robots))
        self.assertNotIn("/thanks/", (ROOT / "sitemap.xml").read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
