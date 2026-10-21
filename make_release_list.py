"""
List the site's releases, for the Versions page.

A release is a version tag (1.0.0, v1.0.0, 1.0.0-rc1): publish.yml publishes
each one at /<tag>/ and the latest at the root. This script writes, newest
first:

  _data/releases.json
    { "pages_url": "https://caresets.github.io/caresets",
      "download_url": "https://github.com/caresets/caresets/releases/download",
      "releases": [ { "tag": "v0.9.1", "date": "2026-10-21",
                      "content_version": "0.9.0", "title": "...",
                      "notes": "<markdown>", "current": true }, ... ] }

  tag, date        from git: the tag, and the day its GitHub release was
                   published (or, without one, the day the tag was made)
  content_version  VERSION as it was at that tag
  title, notes     from the GitHub release of that tag, when there is one;
                   the release notes are written there (see the cut-release
                   skill), so this is the only place they live

`current` marks the highest version, which is what the root serves. The site links
are absolute, so the page works on the RIZIV-INAMI copy too.

Needs the tags locally: in CI, `git fetch --tags`. Reads the GitHub API with
GH_TOKEN or GITHUB_TOKEN when set, and without a token for a public
repository; if the API cannot be reached the list is written without notes,
since the table is still right without them.

  python make_release_list.py
"""

import io
import json
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "_data", "releases.json")

# The same tags publish.yml treats as releases: v[0-9]* and [0-9]*.
RELEASE_TAG = re.compile(r"^v?[0-9]")


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8").stdout


def repository():
    """owner/repo: from the Actions environment, else from the origin remote."""
    if os.environ.get("GITHUB_REPOSITORY"):
        return os.environ["GITHUB_REPOSITORY"]
    url = git("remote", "get-url", "origin").strip()
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url)
    return m.group(1) if m else ""


def github_releases(repo):
    """{tag: release} from the GitHub API, or {} if it cannot be read."""
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(
        "https://api.github.com/repos/%s/releases?per_page=100" % repo, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {r["tag_name"]: r for r in json.load(resp)}
    except Exception as e:  # the table is still right without the notes
        print("  ! release notes not read (%s); listing without them" % e)
        return {}


def main():
    repo = repository()
    owner, _, name = repo.partition("/")
    pages_url = ("https://%s.github.io" % owner.lower()
                 + ("" if name.lower().endswith(".github.io") else "/" + name))

    lines = git("for-each-ref", "refs/tags", "--sort=-creatordate",
                "--format=%(refname:short)\t%(creatordate:short)").splitlines()
    tags = [l.split("\t") for l in lines if l and RELEASE_TAG.match(l)]
    published = github_releases(repo) if repo else {}

    releases = []
    for tag, date in tags:
        rel = published.get(tag) or {}
        releases.append({
            "tag": tag,
            "date": (rel.get("published_at") or "")[:10] or date,
            "content_version": git("show", "%s:VERSION" % tag).strip(),
            "title": (rel.get("name") or "").strip(),
            "notes": (rel.get("body") or "").replace("\r\n", "\n").strip(),
            "prerelease": bool(rel.get("prerelease")),
            "current": not releases,
        })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"pages_url": pages_url,
                   "download_url": "https://github.com/%s/releases/download" % repo,
                   "releases": releases}, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    sys.stdout.reconfigure(encoding="utf-8")
    print("Wrote %s: %d release(s)%s" % (
        os.path.relpath(OUT, ROOT).replace("\\", "/"), len(releases),
        ", current " + releases[0]["tag"] if releases else ""))


if __name__ == "__main__":
    main()
