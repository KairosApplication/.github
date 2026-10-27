"""Synchronize documentation using an explicitly validated repository identity."""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import posixpath
import re
import subprocess
import urllib.request
from urllib.parse import quote, unquote, urlparse

import java_documentation as java

README_NAMES = ("README.md", "readme.md", "Readme.md")


def notice(message, warning=False):
    if warning:
        escaped = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::warning::{escaped}")
    else:
        print(message)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as output:
            output.write(f"- {message}\n")


def output_paths(paths):
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            stream.write("paths<<DOCS_BOT_PATHS\n" + "\n".join(paths) + "\nDOCS_BOT_PATHS\n")


def git(path, *args, authenticated=False):
    env = os.environ.copy()
    if authenticated:
        credential = base64.b64encode(
            ("x-access-token:" + env["DOCS_BOT_TOKEN"]).encode()
        ).decode()
        env.update(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="http.https://github.com/.extraheader",
                   GIT_CONFIG_VALUE_0="AUTHORIZATION: basic " + credential)
    return subprocess.run(["git", "-C", str(path), *args], env=env,
                          check=True, text=True, capture_output=True).stdout.strip()


def validate_identity(path, repository, organization, wiki=False):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Invalid target repository")
    owner, name = repository.split("/")
    if owner.lower() != organization.lower() or name == ".github":
        raise ValueError("Target must be another repository of this organization")
    expected = f"https://github.com/{repository}{'.wiki' if wiki else ''}.git"
    actual = git(path, "remote", "get-url", "origin").rstrip("/")
    if actual.removesuffix(".git").lower() != expected.removesuffix(".git").lower():
        raise ValueError(f"Repository identity mismatch: expected {expected}")


def section(text, body):
    if java.START in text or java.END in text:
        return java.marked_section(text, body, "")
    return text.rstrip() + f"\n\n{java.START}\n{body.rstrip()}\n{java.END}\n"


def documents(root):
    docs = root / "docs"
    if not docs.exists():
        return []
    result = []
    for path in sorted(docs.rglob("*.md")):
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("Documentation path escapes target checkout")
        result.append(path)
    return result


def readme_path(root):
    entries = {path.name: path for path in root.iterdir()}
    return next((entries[name] for name in README_NAMES
                 if name in entries and entries[name].is_file()), None)


def changed_documentation_paths(root):
    # Only pass existing, actually changed files to git add. Literal alternatives
    # such as readme.md fail on Linux when this repo only contains README.md.
    allowed = set(README_NAMES) | {"docs/api-endpoints.md"}
    changed = set(git(root, "diff", "--name-only", "HEAD").splitlines())
    changed.update(git(root, "ls-files", "--others", "--exclude-standard").splitlines())
    return sorted(path for path in changed & allowed if (root / path).is_file())


def source_url(repository, branch, relative):
    return f"https://github.com/{repository}/blob/{quote(branch, safe='')}/{quote(relative, safe='/')}"


def title(path):
    return next((line[2:].strip() for line in java.read_file(path)[0].splitlines()
                 if line.startswith("# ")), path.stem).replace("[", "").replace("]", "")


def generate(root):
    readme = readme_path(root)
    if not readme:
        print("No Markdown README; skipping README generation")
        return
    if readme.is_symlink():
        raise ValueError("README must not be a symbolic link")
    documents(root)  # Validate existing documentation before generating any file.
    if (root / "docs").is_symlink() or (root / "docs/api-endpoints.md").is_symlink():
        raise ValueError("Generated documentation must stay inside the target checkout")
    java.ROOT = root
    java.DOCS = root / "docs"
    java.CONTROLLERS = root / "src/main/java/com/kairos/kairosapipostgres/controller"
    java.SECURITY = root / "src/main/java/com/kairos/kairosapipostgres/config/SecurityConfig.java"
    facts = []
    if java.CONTROLLERS.is_dir() and java.SECURITY.is_file() and (root / "pom.xml").is_file():
        routes = java.endpoints()
        jdk, boot = java.project_versions()
        java.DOCS.mkdir(exist_ok=True)
        java.write_if_changed(java.DOCS / "api-endpoints.md", java.api_reference(routes))
        facts = [f"Java **{jdk}**, Spring Boot **{boot}**, **{len(routes)}** rotas mapeadas.", ""]
    paths = documents(root)
    if not paths:
        print("No docs/*.md; leaving README unchanged")
        return
    body = "\n".join(["## Documentação", "", *facts,
                      *[f"- [{title(p)}]({quote(p.relative_to(root).as_posix(), safe='/')})" for p in paths]])
    current, newline = java.read_file(readme)
    java.write_if_changed(readme, section(current, body), newline)


def wiki_text(text, repository, branch, relative):
    # Resolve Markdown relative links against THIS source file, not the hub repository.
    def replace(match):
        label, destination = match.groups()
        if destination.startswith(("#", "//")) or urlparse(destination).scheme:
            return match.group(0)
        parsed = urlparse(destination)
        path = unquote(parsed.path)
        path = posixpath.normpath(path.lstrip("/") if path.startswith("/") else
                                  posixpath.join(posixpath.dirname(relative), path))
        if path == ".." or path.startswith("../"):
            raise ValueError("Relative documentation link escapes target repository")
        url = source_url(repository, branch, path)
        if parsed.query:
            url += "?" + parsed.query
        if parsed.fragment:
            url += "#" + parsed.fragment
        return f"[{label}]({url})"
    return re.sub(r"\[([^\]]*)\]\(([^\s)]+)\)", replace, text)


def update_wiki(root, wiki, repository, organization, branch):
    validate_identity(root, repository, organization)
    validate_identity(wiki, repository, organization, wiki=True)
    home = wiki / "Home.md"
    if not home.is_file() or home.is_symlink():
        raise ValueError("Existing wiki must have a regular Home.md")
    readme = readme_path(root)
    if readme and readme.is_symlink():
        raise ValueError("README must not be a symbolic link")
    paths = ([readme] if readme else []) + documents(root)
    pages = []
    for source in paths:
        relative = source.relative_to(root).as_posix()
        # Hex encoding is collision-free even for nested paths or case differences.
        page = "Bot-README" if source == readme else "Bot-Doc-" + relative.encode().hex()
        destination = wiki / (page + ".md")
        marker = f"<!-- docs-bot:source {repository}/{relative} -->"
        if destination.exists() and (destination.is_symlink() or marker not in java.read_file(destination)[0]):
            raise ValueError(f"Refusing to overwrite unmanaged wiki page: {page}")
        text = java.read_file(source)[0]
        body = f"{marker}\n\nFonte: [{relative}]({source_url(repository, branch, relative)})\n\n"
        java.write_if_changed(destination, body + wiki_text(text, repository, branch, relative))
        pages.append(f"- [{title(source)}]({page})")
    text, newline = java.read_file(home)
    body = "\n".join(["## Documentação sincronizada", "",
                      f"Origem: `{repository}` — branch `{branch}`. Apenas conteúdo já integrado.", "", *pages])
    java.write_if_changed(home, section(text, body), newline)


def api(path):
    request = urllib.request.Request("https://api.github.com" + path, headers={
        "Authorization": "Bearer " + os.environ["DOCS_BOT_TOKEN"],
        "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def list_repositories(organization, requested):
    repos = []
    page = 1
    while True:
        batch = api(f"/orgs/{quote(organization, safe='')}/repos?per_page=100&page={page}")
        if not batch:
            break
        repos.extend(batch)
        page += 1
    targets = [{"repository": r["full_name"], "branch": r["default_branch"], "wiki": r["has_wiki"]}
               for r in repos if r["name"] != ".github" and not r["archived"]
               and not r["disabled"] and not r["fork"] and r["size"] > 0
               and (not requested or r["full_name"].lower() == requested.lower())]
    if requested and not targets:
        raise ValueError("Requested target is not an eligible repository in this organization")
    documented_targets = []
    for target in targets:
        tree = api(f"/repos/{target['repository']}/git/trees/{quote(target['branch'], safe='')}")
        entries = tree["tree"]
        if tree.get("truncated"):
            raise ValueError(f"Incomplete root tree for {target['repository']}")
        if any((entry["path"] in README_NAMES and entry["type"] == "blob"
                and entry["mode"] in {"100644", "100755"}) or
               (entry["path"] == "docs" and entry["type"] == "tree") for entry in entries):
            documented_targets.append(target)
        else:
            notice(f"{target['repository']}: no Markdown README or docs/; nothing to synchronize")
            if any(entry["mode"] == "160000" for entry in entries) and not any(
                    entry["path"] == ".gitmodules" for entry in entries):
                notice(f"{target['repository']}: submodule entry without .gitmodules; repair the repository before enabling its checkout", warning=True)
    targets = documented_targets
    if len(targets) > 256:
        raise ValueError("More than 256 targets: split the organization into multiple matrices")
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write("matrix=" + json.dumps({"include": targets}) + "\n")
        output.write(f"count={len(targets)}\n")


def sync_wiki(root, wiki, repository, organization, branch):
    validate_identity(root, repository, organization)
    wiki.mkdir(parents=True, exist_ok=True)
    url = f"https://github.com/{repository}.wiki.git"
    try:
        refs = git(root, "ls-remote", url, authenticated=True)
    except subprocess.CalledProcessError:
        notice(f"{repository}: wiki unavailable. Initialize Home or check token access/network. README synchronization continues.", warning=True)
        return
    if not refs:
        notice(f"{repository}: wiki has no pages; initialize Home. README synchronization continues.", warning=True)
        return
    try:
        git(wiki, "clone", url, ".", authenticated=True)
    except subprocess.CalledProcessError:
        notice(f"{repository}: wiki clone failed. Check access/network. README synchronization continues.", warning=True)
        return
    # Identity mismatches and malformed content remain fatal: do not suppress them.
    validate_identity(wiki, repository, organization, wiki=True)
    if not (wiki / "Home.md").exists():
        notice(f"{repository}: wiki has no Home.md; initialize Home. README synchronization continues.", warning=True)
        return
    update_wiki(root, wiki, repository, organization, branch)
    if git(wiki, "status", "--porcelain"):
        git(wiki, "config", "user.name", "documentation-bot")
        git(wiki, "config", "user.email", "documentation-bot@users.noreply.github.com")
        paths = ["Home.md", *[path.name for path in sorted(wiki.glob("Bot-*.md"))]]
        git(wiki, "add", "--", *paths)
        git(wiki, "commit", "-m", f"docs: sync documentation from {repository}")
        try:
            git(wiki, "push", "origin", "HEAD", authenticated=True)
        except subprocess.CalledProcessError:
            notice(f"{repository}: wiki publication failed. Check Contents/write permission and concurrent edits. README synchronization continues.", warning=True)
            return
    notice(f"{repository}: wiki synchronized from its default branch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["list", "wiki", "generate"])
    parser.add_argument("--root", type=Path)
    parser.add_argument("--wiki", type=Path)
    args = parser.parse_args()
    organization = os.environ["ORGANIZATION"]
    repository = os.environ.get("TARGET_REPOSITORY", "")
    if args.command == "list":
        list_repositories(organization, repository)
        return
    root = args.root.resolve()
    validate_identity(root, repository, organization)
    branch = os.environ["TARGET_BRANCH"]
    if git(root, "rev-parse", "HEAD") != git(root, "rev-parse", f"refs/remotes/origin/{branch}"):
        raise ValueError("Target checkout is not the fetched default-branch snapshot")
    if args.command == "generate":
        generate(root)
        paths = changed_documentation_paths(root)
        output_paths(paths)
        if not paths:
            notice(f"{repository}: no README/reference changes to propose")
        return
    sync_wiki(root, args.wiki.resolve(), repository, organization, branch)


if __name__ == "__main__":
    main()
