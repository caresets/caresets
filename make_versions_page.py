"""
Write the Versions page at the root of the published site: /versions/.

One page, at one address, listing every copy the site is published as:

  the releases     newest first, each with its date, content version and
                   release notes, a link to its copy and its two zips; the
                   newest is the one at the root (the published version)
  dev/             the development version, built from main
  branches/<x>/    the branch previews currently up

publish.yml runs this in its deploy step, on the gh-pages checkout, every
time anything is published, and again when a branch preview is removed - so
the page is always current, whichever copy changed. The page is plain HTML
written here, not a Jekyll page: no copy of the site owns it, and a release
replacing the root leaves it alone.

  release tags     from git: v[0-9]* and [0-9]* (the tags publish.yml
                   publishes), so the tags must be fetched first
  content version  VERSION as it was at the tag
  title, notes     from the tag's GitHub release, when there is one (written
                   there by whoever made the release; see the cut-release
                   skill); without the API the page lists them without notes
  previews         the folders under <pages>/branches/

Reads the GitHub API with GH_TOKEN or GITHUB_TOKEN when set.

  python make_versions_page.py <gh-pages checkout>      writes <dir>/versions/index.html
  python make_versions_page.py --json                   prints the release list
"""

import argparse
import html
import io
import json
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))

# The same tags publish.yml treats as releases.
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
    except Exception as e:  # the list is still right without the notes
        print("  ! release notes not read (%s); listing without them" % e)
        return {}


def collect():
    repo = repository()
    owner, _, name = repo.partition("/")
    pages_url = ("https://%s.github.io" % owner.lower()
                 + ("" if name.lower().endswith(".github.io") else "/" + name))

    # Newest version first, a pre-release (1.0.0-rc1) before its release.
    # Sorted by version, not date: a tag made by a GitHub release is a plain
    # tag, which carries no date of its own.
    lines = git("-c", "versionsort.suffix=-", "for-each-ref", "refs/tags",
                "--sort=-v:refname",
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
    return {"repo": repo, "pages_url": pages_url,
            "download_url": "https://github.com/%s/releases/download" % repo,
            "releases": releases}


def notes_html(text):
    """The little Markdown release notes use: paragraphs, line breaks,
    **bold**, `code`, [links](https://...) and - lists."""
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.split("\n")
        if all(re.match(r"\s*[-*] ", l) for l in lines):
            items = "".join("<li>%s</li>" % inline(re.sub(r"^\s*[-*] ", "", l)) for l in lines)
            out.append("<ul>%s</ul>" % items)
        else:
            out.append("<p>%s</p>" % "<br>".join(inline(l) for l in lines))
    return "".join(out)


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return s


def page(data, pages_dir):
    esc = html.escape
    base = data["pages_url"]
    rows = []
    for r in data["releases"]:
        badges = "".join("<br><em>%s</em>" % b for b, on in
                         (("current", r["current"]), ("pre-release", r["prerelease"])) if on)
        title = ("<strong>%s</strong>" % esc(r["title"])
                 if r["title"] and r["title"] != r["tag"] else "")
        dl = "%s/%s" % (data["download_url"], r["tag"])
        rows.append(
            "<tr><td><strong>{tag}</strong>{badges}</td><td>{date}</td><td>{cv}</td>"
            "<td>{title}{notes}</td>"
            "<td><a href=\"{base}/{tag}/en/\">EN</a> · <a href=\"{base}/{tag}/fr/\">FR</a> · "
            "<a href=\"{base}/{tag}/nl/\">NL</a><br>"
            "<a href=\"{dl}/caresets-site.zip\">caresets-site.zip</a><br>"
            "<a href=\"{dl}/riziv-inami-site.zip\">riziv-inami-site.zip</a></td></tr>".format(
                tag=esc(r["tag"]), badges=badges, date=esc(r["date"]),
                cv=esc(r["content_version"]), title=title, notes=notes_html(r["notes"]),
                base=base, dl=dl))
    releases = ("<table><thead><tr><th>Release</th><th>Date</th><th>Content</th>"
                "<th>Release notes</th><th>Open</th></tr></thead><tbody>%s</tbody></table>"
                % "".join(rows)) if rows else "<p><em>No release yet.</em></p>"

    previews = sorted(d for d in os.listdir(os.path.join(pages_dir, "branches"))
                      if os.path.isdir(os.path.join(pages_dir, "branches", d))) \
        if os.path.isdir(os.path.join(pages_dir, "branches")) else []
    others = []
    if os.path.isdir(os.path.join(pages_dir, "dev")):
        others.append("<li><a href=\"%s/dev/en/\">Development version</a> — everything "
                      "accepted on <code>main</code> since the last release</li>" % base)
    for d in previews:
        others.append("<li><a href=\"%s/branches/%s/en/\">Branch preview: %s</a></li>"
                      % (base, esc(d), esc(d)))
    others_html = ("<ul>%s</ul>" % "".join(others)) if others else "<p><em>None.</em></p>"

    current = data["releases"][0]["tag"] if data["releases"] else ""
    return PAGE.format(base=base, current=esc(current), releases=releases,
                       others=others_html, repo=esc(data["repo"]))


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Versions - BeSafeShare CareSets</title>
<link rel="icon" href="{base}/favicon.ico">
<style>
  :root {{ --fg: #1f2937; --muted: #6b7280; --line: #d1d5db; --head: #1c7c8f; --bg: #fff; --row: #f9fafb; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --fg: #e5e7eb; --muted: #9ca3af; --line: #374151; --head: #1c7c8f; --bg: #111827; --row: #1f2937; }}
  }}
  body {{ margin: 0; background: var(--bg); color: var(--fg);
         font: 16px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }}
  main {{ max-width: 72rem; margin: 0 auto; padding: 2rem 1rem 4rem; }}
  h1 {{ margin: 0 0 .25rem; }} h2 {{ margin-top: 2.5rem; }}
  .lead {{ color: var(--muted); margin: 0 0 1.5rem; }}
  a {{ color: var(--head); }}
  .wrap {{ overflow-x: auto; }}
  table {{ border-collapse: collapse; width: 100%; min-width: 40rem; }}
  th {{ background: var(--head); color: #fff; text-align: left; }}
  th, td {{ padding: .5rem .75rem; border-bottom: 1px solid var(--line); vertical-align: top; }}
  tbody tr:nth-child(even) {{ background: var(--row); }}
  td p {{ margin: 0 0 .5rem; }} td p:last-child {{ margin: 0; }}
  td ul {{ margin: 0; padding-left: 1.2rem; }}
  em {{ color: var(--muted); }}
</style>
</head>
<body>
<main>
<h1>Versions</h1>
<p class="lead">BeSafeShare CareSets — glossary and logical data models.
The <a href="{base}/en/">published site</a> is release <strong>{current}</strong>.
Every release stays available as it was published.</p>

<h2>Releases</h2>
<p class="lead">"Content" is the version of the glossary and models the release carries.</p>
<div class="wrap">{releases}</div>

<h2>Work in progress</h2>
<p class="lead">Not published: copies to check changes before a release.</p>
{others}

<p class="lead" style="margin-top:3rem">Releases on GitHub:
<a href="https://github.com/{repo}/releases">github.com/{repo}/releases</a></p>
</main>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", nargs="?", help="the gh-pages checkout to write versions/ into")
    ap.add_argument("--json", action="store_true", help="print the release list and stop")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    data = collect()
    if args.json or not args.pages:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    out = os.path.join(args.pages, "versions", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(page(data, args.pages))
    print("Wrote %s: %d release(s)%s" % (
        out, len(data["releases"]),
        ", current " + data["releases"][0]["tag"] if data["releases"] else ""))


if __name__ == "__main__":
    main()
