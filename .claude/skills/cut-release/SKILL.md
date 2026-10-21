---
name: cut-release
description: Cut a new release of the CareSets site - choose the version, draft the release notes from what changed since the last release, get them approved, create the GitHub release (which tags main and publishes it at the site root and /<tag>/), and check the result. Use when asked to release, publish, cut or tag a new version of the site, to write or edit release notes, or to update the Versions page.
---

# Cut a release

A release is a version tag on `main` (`v0.9.1`, `v1.0.0`, `v1.0.0-rc1`). Pushing
it makes `.github/workflows/publish.yml` publish that commit twice: at the site
root (the current published version) and at `/<tag>/` (kept for good). Pushes
to `main` only ever update `/dev/`, so **nothing reaches the published site
without a release**.

The release notes are the body of the GitHub release. That is their only home:
`make_release_list.py` reads them for the Versions page (`/<lang>/versions/`),
so a release created **with** its notes shows them on its own build.

Work through the steps in order and stop for the user's decision where marked.

## 1. Check main is ready

```sh
git fetch origin --tags
git status -sb                      # on main, clean, not behind origin/main
gh run list --branch main --limit 3 # the last run on main succeeded
```

Ask the user to look at https://caresets.github.io/caresets/dev/ — that is
exactly what the release will publish. Do not release from a branch.

## 2. See what changed since the last release

```sh
prev=$(git -c versionsort.suffix=- tag -l 'v[0-9]*' '[0-9]*' --sort=-v:refname | head -1)
git log --oneline --no-merges "$prev"..origin/main | grep -v 'chore: regenerate content'
git diff --stat "$prev"..origin/main -- input/ _resources/glossary/ VERSION
ls glossary-changes/                # glossary change notes newer than $prev
```

Sort what you find into:

- **Content** — glossary terms added, changed, removed (the
  `glossary-changes/*.md` notes list them term by term); logical models added
  or updated (`input/models/`); mappings.
- **Site** — pages, layout, navigation, fixes.

## 3. Choose the version — **user decides**

Propose one and ask:

- Content changed → the content version (`VERSION`) should change too. It is
  stamped into the CodeSystems and ConceptMap, so bumping it is a content
  change of its own: edit `VERSION` and `content_version` in `_config.yml`,
  commit to `main` ("Raise the content version to X"), push, and wait for
  `/dev/` to show it before going on.
- Only the site changed → keep `VERSION`, raise the tag's last number
  (`v0.9.1` → `v0.9.2`).

Never move or re-create an existing tag: a published release stays as it was.
A fix is a new release.

## 4. Draft the release notes — **user approves**

Short Markdown, in English unless the user asks otherwise; the Versions page
shows them as written, in every language. Shape:

```markdown
Glossary: added Specimen; revised the French definition of CareSet.
Models: updated BeModelAllergyIntolerance to 1.2.0.

Site: the Home link in the top menu now opens the published site.
```

- Name terms and models; say what changed, not which files.
- Leave out build noise (timestamps, regenerated files, backups).
- Show the draft to the user and apply only what they approve. Do not create
  the release with notes they have not seen.

Save the approved text to a file in the scratchpad (`notes.md`).

## 5. Create the release

Creating the GitHub release creates the tag on `main`, which starts the
publish run with the notes already in place:

```sh
gh release create v0.9.2 --target "$(git rev-parse origin/main)" \
  --title v0.9.2 --notes-file notes.md --latest
```

The run attaches `caresets-site.zip` and `riziv-inami-site.zip` to the
release a few minutes later.

## 6. Check the result

```sh
gh run list --branch v0.9.2 --limit 1     # build and deploy succeeded
```

Then, once GitHub's own "pages build and deployment" run has finished
(usually 1-2 minutes; if it sits "in progress" for long, it is GitHub's side):

- https://caresets.github.io/caresets/en/ — footer reads "Release v0.9.2",
  no banner.
- https://caresets.github.io/caresets/v0.9.2/en/ — grey "Release v0.9.2"
  banner.
- https://caresets.github.io/caresets/en/versions/ — v0.9.2 is first,
  marked current, with the notes; earlier releases below it.
- The release on GitHub has both zips.

Report what you checked and what you saw.

## Editing notes afterwards

```sh
gh release edit v0.9.2 --notes-file notes.md
```

The Versions page picks the change up on the next build: `/dev/` on the next
push to `main`, the root only at the next release (the root is rebuilt only
by a release).
