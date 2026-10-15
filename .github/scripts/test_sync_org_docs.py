import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sync_org_docs as bot


class DocumentationTests(unittest.TestCase):
    def test_wrong_readme_repository_rejected(self):
        with patch.object(bot, "git", return_value="https://github.com/KairosApplication/other.git"):
            with self.assertRaises(ValueError):
                bot.validate_identity(Path("target"), "KairosApplication/api", "KairosApplication")

    def test_wrong_wiki_repository_rejected(self):
        with patch.object(bot, "git", return_value="https://github.com/KairosApplication/other.wiki.git"):
            with self.assertRaises(ValueError):
                bot.validate_identity(Path("wiki"), "KairosApplication/api", "KairosApplication", wiki=True)

    def test_foreign_organization_and_hub_rejected(self):
        for repo in ["AnotherOrganization/api", "KairosApplication/.github", "../../api"]:
            with self.assertRaises(ValueError):
                bot.validate_identity(Path("target"), repo, "KairosApplication")

    def test_correct_pair_accepted(self):
        with patch.object(bot, "git", side_effect=["https://github.com/KairosApplication/api.git",
                                                  "https://github.com/KairosApplication/api.wiki.git"]):
            bot.validate_identity(Path("target"), "KairosApplication/api", "KairosApplication")
            bot.validate_identity(Path("wiki"), "KairosApplication/api", "KairosApplication", wiki=True)

    def test_generate_preserves_manual_readme_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_bytes(b"# Manual\r\n\r\nKeep me\r\n")
            (root / "docs").mkdir()
            (root / "docs/guide.md").write_text("# Guide\n", encoding="utf-8")
            bot.generate(root)
            once = (root / "README.md").read_bytes()
            bot.generate(root)
            self.assertEqual(once, (root / "README.md").read_bytes())
            self.assertTrue(once.startswith(b"# Manual\r\n\r\nKeep me\r\n"))
            self.assertIn(b"[Guide](docs/guide.md)", once)

    def test_missing_docs_keeps_readme(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("# Manual\n", encoding="utf-8")
            bot.generate(root)
            self.assertEqual("# Manual\n", (root / "README.md").read_text())

    def test_wiki_preserves_manual_pages_and_target_links(self):
        with tempfile.TemporaryDirectory() as temp:
            root, wiki = Path(temp) / "target", Path(temp) / "wiki"
            root.mkdir(); wiki.mkdir()
            (root / "README.md").write_text("# API\n[Guide](docs/guide.md)\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs/guide.md").write_text("# Guide\n[README](../README.md)\n", encoding="utf-8")
            (wiki / "Home.md").write_text("# Existing wiki\nManual home\n", encoding="utf-8")
            (wiki / "Manual.md").write_text("Manual page\n", encoding="utf-8")
            with patch.object(bot, "validate_identity") as identity:
                bot.update_wiki(root, wiki, "KairosApplication/api", "KairosApplication", "main")
                self.assertEqual(identity.call_count, 2)
                self.assertEqual(identity.call_args_list[1].args[:2], (wiki, "KairosApplication/api"))
            before = {p.name: p.read_bytes() for p in wiki.glob("*.md")}
            with patch.object(bot, "validate_identity"):
                bot.update_wiki(root, wiki, "KairosApplication/api", "KairosApplication", "main")
            self.assertEqual(before, {p.name: p.read_bytes() for p in wiki.glob("*.md")})
            self.assertTrue((wiki / "Home.md").read_text().startswith("# Existing wiki\nManual home\n"))
            self.assertEqual("Manual page\n", (wiki / "Manual.md").read_text())
            self.assertIn("https://github.com/KairosApplication/api/blob/main/docs/guide.md",
                          (wiki / "Bot-README.md").read_text())
            guide = next(wiki.glob("Bot-Doc-*.md")).read_text()
            self.assertIn("https://github.com/KairosApplication/api/blob/main/README.md", guide)

    def test_unmanaged_wiki_page_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root, wiki = Path(temp) / "target", Path(temp) / "wiki"
            root.mkdir(); wiki.mkdir()
            (root / "README.md").write_text("# API\n", encoding="utf-8")
            (wiki / "Home.md").write_text("# Home\n", encoding="utf-8")
            (wiki / "Bot-README.md").write_text("Manual content\n", encoding="utf-8")
            with patch.object(bot, "validate_identity"), self.assertRaises(ValueError):
                bot.update_wiki(root, wiki, "KairosApplication/api", "KairosApplication", "main")
            self.assertEqual("Manual content\n", (wiki / "Bot-README.md").read_text())

    def test_invalid_markers_fail(self):
        with self.assertRaises(ValueError):
            bot.section("Manual\n<!-- docs-bot:start -->", "Generated")

    def test_root_links_stay_in_target_repository(self):
        text = bot.wiki_text("[Guide](/docs/guide.md#setup)", "KairosApplication/api", "release/docs", "README.md")
        self.assertEqual("[Guide](https://github.com/KairosApplication/api/blob/release%2Fdocs/docs/guide.md#setup)", text)

    def test_relative_link_cannot_escape_repository(self):
        with self.assertRaises(ValueError):
            bot.wiki_text("[Other](../../other/README.md)", "KairosApplication/api", "main", "README.md")

    def test_discovery_filters_targets_and_dispatch(self):
        repos = [dict(full_name="KairosApplication/api", name="api", default_branch="main",
                      has_wiki=True, archived=False, disabled=False, fork=False, size=1),
                 dict(full_name="KairosApplication/.github", name=".github", default_branch="main",
                      has_wiki=True, archived=False, disabled=False, fork=False, size=1)]
        with tempfile.TemporaryDirectory() as temp:
            output = str(Path(temp) / "output")
            with patch.object(bot, "api", side_effect=[repos, []]), patch.dict(os.environ, GITHUB_OUTPUT=output):
                bot.list_repositories("KairosApplication", "KairosApplication/api")
            matrix = json.loads(Path(output).read_text().splitlines()[0].split("=", 1)[1])
            self.assertEqual(matrix["include"][0]["repository"], "KairosApplication/api")
            self.assertEqual(len(matrix["include"]), 1)


if __name__ == "__main__":
    unittest.main()
