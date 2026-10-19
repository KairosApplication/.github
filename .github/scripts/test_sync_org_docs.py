import json
import os
from pathlib import Path
import tempfile
import subprocess
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
            tree = {"tree": [{"path": "README.md", "type": "blob", "mode": "100644"}]}
            with patch.object(bot, "api", side_effect=[repos, [], tree]), patch.dict(os.environ, GITHUB_OUTPUT=output):
                bot.list_repositories("KairosApplication", "KairosApplication/api")
            matrix = json.loads(Path(output).read_text().splitlines()[0].split("=", 1)[1])
            self.assertEqual(matrix["include"][0]["repository"], "KairosApplication/api")
            self.assertEqual(len(matrix["include"]), 1)

    def test_only_real_changed_paths_are_staged_with_any_readme_case(self):
        for name in bot.README_NAMES:
            for with_reference in (False, True):
                with self.subTest(name=name, with_reference=with_reference), tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    bot.git(root, "init")
                    (root / name).write_text("# Manual README\n", encoding="utf-8")
                    (root / "docs").mkdir()
                    (root / "docs/guide.md").write_text("# Guide\n", encoding="utf-8")
                    bot.git(root, "add", ".")
                    bot.git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                            "commit", "-m", "initial fixture")
                    if with_reference:
                        (root / "docs/api-endpoints.md").write_text("# Routes\n", encoding="utf-8")
                    (root / "unrelated.txt").write_text("must not be staged", encoding="utf-8")
                    bot.generate(root)
                    paths = bot.changed_documentation_paths(root)
                    expected = {name} | ({"docs/api-endpoints.md"} if with_reference else set())
                    self.assertEqual(expected, set(paths))
                    bot.git(root, "add", "--", *paths)
                    self.assertEqual(expected, set(bot.git(root, "diff", "--cached", "--name-only").splitlines()))

    def test_inaccessible_wiki_does_not_prevent_readme_update(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("# Manual README\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs/guide.md").write_text("# Guide\n", encoding="utf-8")
            failure = subprocess.CalledProcessError(128, ["git", "ls-remote"])
            with patch.object(bot, "git", side_effect=["https://github.com/KairosApplication/api.git", failure]), patch.object(bot, "notice") as notice:
                bot.sync_wiki(root, root / "wiki", "KairosApplication/api", "KairosApplication", "main")
                self.assertTrue(notice.call_args.kwargs["warning"])
            bot.generate(root)
            self.assertIn("[Guide](docs/guide.md)", (root / "README.md").read_text())

    def test_wiki_identity_mismatch_is_still_fatal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(bot, "git", return_value="https://github.com/KairosApplication/other.git"):
                with self.assertRaises(ValueError):
                    bot.sync_wiki(root, root / "wiki", "KairosApplication/api", "KairosApplication", "main")

    def test_wiki_push_failure_is_reported_without_claiming_success(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wiki = root / "wiki"
            wiki.mkdir()
            (wiki / "Home.md").write_text("# Home\n", encoding="utf-8")
            def fake_git(path, *args, **kwargs):
                if args[0] == "ls-remote":
                    return "abc refs/heads/master"
                if args[0] == "status":
                    return " M Home.md"
                if args[0] == "push":
                    raise subprocess.CalledProcessError(128, ["git", "push"])
                return ""
            with patch.object(bot, "git", side_effect=fake_git), patch.object(bot, "validate_identity"), patch.object(bot, "update_wiki"), patch.object(bot, "notice") as notice:
                bot.sync_wiki(root, wiki, "KairosApplication/api", "KairosApplication", "main")
                self.assertEqual(notice.call_count, 1)
                self.assertIn("publication failed", notice.call_args.args[0])
                self.assertTrue(notice.call_args.kwargs["warning"])

    def test_discovery_skips_docless_repo_with_invalid_submodule(self):
        repo = dict(full_name="KairosApplication/landing", name="landing", default_branch="main",
                    has_wiki=True, archived=False, disabled=False, fork=False, size=1)
        tree = {"tree": [{"path": "landing", "type": "commit", "mode": "160000"}]}
        with tempfile.TemporaryDirectory() as temp:
            output = str(Path(temp) / "output")
            with patch.object(bot, "api", side_effect=[[repo], [], tree]), patch.dict(os.environ, GITHUB_OUTPUT=output), patch.object(bot, "notice") as notice:
                bot.list_repositories("KairosApplication", "")
            self.assertIn("count=0", Path(output).read_text())
            self.assertTrue(any("submodule" in call.args[0] for call in notice.call_args_list))


if __name__ == "__main__":
    unittest.main()
