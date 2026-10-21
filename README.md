# BeSafeShare Documentation Site

Source for the BeSafeShare **glossary** and **logical data model** documentation, built with Jekyll and the [Just-the-docs](https://pmarsceill.github.io/just-the-docs) theme.

## TL;DR for maintainers

**Working from a browser, without Python or an IDE?** Read [EDITING-GUIDE.md](EDITING-GUIDE.md): changing the glossary, the pages and the models, reviewing, and publishing a release, all on GitHub.

**Two things are authored, and they are both Excel workbooks.** Everything else
in this repository is generated from them or arrives from the publication
process.

| You edit | It becomes | Run |
|---|---|---|
| `input/Glossaire CareSets V1.xlsx` | the glossary CSVs, then the published CodeSystems | `python build_content.py` |
| `models/xls/<Model>.xlsx` | a StructureDefinition to hand to publication | `python import_logical_model_xlsx.py` |

`input/ClinicalGlossary.csv` is **generated** from the workbook — editing it by
hand works until the next build overwrites it. `OperationalGlossary.csv` has no
workbook behind it and is still edited directly.

### The glossary

1. Edit `input/Glossaire CareSets V1.xlsx` — one row per term, with
   `Definition` and `Description` in FR, NL and EN. The definition is the
   definition; the description is the note to entry. They stay separate all the
   way to the published CodeSystem.
2. `python build_content.py`
3. Commit. The GitHub Action publishes.

The `Item` column is the human label (`Business Identifier`); the code used by
the CodeSystem and the mappings is that with the spaces removed
(`BusinessIdentifier`), derived automatically. Renaming an item therefore
renames a code — check `input/glossary_mappings.csv` when you do.

### The logical models

Models are **authored as workbooks and arrive here already published**:

```
models/xls/<Model>.xlsx            authors write FR + NL; you add and verify EN
      |   python import_logical_model_xlsx.py
      v
models/generated/                  hand this to the publication process
      |   ...published in the eHealth package...
      v
caresets-structuredefinitions-<date>.zip
      |   python import_models_zip.py <the zip>
      v
input/models/                      what the site serves
      |   python build_content.py
      v
_resources/models/
```

`input/models/` holds models that have **been published**. Nothing generates
into it except `import_models_zip.py`, so that an export can never silently
overwrite unpublished work.

English is the base language in the published JSON; French and Dutch travel as
FHIR `translation` extensions. If a language is missing, the base falls back to
French then Dutch, so an untranslated model still publishes in the language it
was written in.

### Mappings

`input/glossary_mappings.csv` (`Model;ElementSuffix;GlossaryCode`) links a model
element to a glossary concept. `Model` is the StructureDefinition's **name**
(`BeModelVaccination`), not a filename — so renaming a file cannot orphan a
mapping.

---

## Update procedure

### 1. Edit the content in `input/`

In the GitHub web UI (or locally, if you prefer):

- **Glossaries** — edit `input/ClinicalGlossary.csv` and/or `input/OperationalGlossary.csv` (`;`-separated).
- **Logical models** — add/edit/remove `input/models/StructureDefinition-*.json` (FHIR `kind: logical`). Work-in-progress models go in `input/models/draft/` and are **not** published until moved up to `input/models/`.
- **Mappings** — edit `input/glossary_mappings.csv` (`Model;ElementSuffix;GlossaryCode`).

See [`input/README.md`](input/README.md) for a field-by-field guide.

### 2. Commit to `main` — the GitHub Action does the rest

Every push triggers [`.github/workflows/publish.yml`](.github/workflows/publish.yml), which builds the site and publishes it to this repository's `gh-pages` branch. GitHub Pages serves that branch at **<https://caresets.github.io/caresets/>**:

| You push | It appears at | What it is |
|---|---|---|
| a release tag, e.g. `v0.9.0` | **`/caresets/`** and `/caresets/v0.9.0/` | the published version, plus a copy of that release kept for good |
| to `main` | `/caresets/dev/` | the development version |
| to another branch `x` | `/caresets/branches/x/` | a preview of that branch (removed when the branch is deleted) |

Every copy except the published one shows a banner saying what it is, and stays out of search results. The footer says which copy you are on (e.g. "Release v0.9.0" or "Development version"); hover over it for the commit and build time.

What the build does first depends on **what you changed**:

- **You edited something in `input/`** (or `VERSION`) → it runs the Python: regenerates `_resources/` (models, glossary, mappings). On `main` it also **snapshots `input/` to `archive/v<VERSION>/`** and commits both back. A release always regenerates.
- **You edited anything else** (a page, layout, CSS…) → it skips Python and just builds what's committed.

Each build also makes two zips, kept on the run as artifacts (90 days):

- **`caresets-site.zip`** — the site exactly as built for its copy.
- **`riziv-inami-site.zip`** — the RIZIV-INAMI deployable, built without the public `url`.

A release also attaches both to a GitHub release named after its tag, so the current release always has the same download links:

- **<https://github.com/caresets/caresets/releases/latest/download/caresets-site.zip>**
- **<https://github.com/caresets/caresets/releases/latest/download/riziv-inami-site.zip>**

You do **not** run any Python locally for the site or the zips — that's the Action's job. (Pull requests are also validated by [`ci.yml`](.github/workflows/ci.yml), which builds but does not deploy.)

A publish from a release replaces the root of `gh-pages`, but never touches `dev/`, `branches/`, earlier release folders, or what [`.github/gh-pages-keep`](.github/gh-pages-keep) lists.

### When you cut a release

1. Bump `VERSION` and `content_version` in `_config.yml` (also editable in the browser), commit to `main`, and check the result at `/caresets/dev/`. The version names the backup snapshot (`archive/v<VERSION>/`).
2. Create the release **with its release notes**: on GitHub, **Releases → Draft a new release**, new tag `v<VERSION>` on `main`, notes in the description, **Publish release**. Only version-like tags (`1.0.0`, `v1.0.0`, `1.0.0-rc1`) publish. With Claude Code, the [`cut-release`](.claude/skills/cut-release/SKILL.md) skill drafts the notes from what changed and does the rest.
3. The notes appear on the **Versions** page (`/en/versions/`, linked from the footer), which lists every release with its date, content version, notes, site and zips.

### Optional: preview locally before committing

Only if you have Ruby + Python installed and want to see changes before pushing:

```sh
python build_content.py    # regenerate _resources/ from input/
bundle exec jekyll serve --config _config.yml,_config_local.yml --watch
```

Open <http://localhost:8002> and hard-refresh (**Ctrl+Shift+R**).


## Backups & versioning

Every published version is snapshotted to `archive/v<VERSION>/` (one folder per version, refreshed if the same version is re-published). This happens automatically on publish; you can also do it by hand:

```sh
python backup_content.py            # snapshot input/ -> archive/v<VERSION>/
python backup_content.py --list     # list available version snapshots
python backup_content.py --restore 0.1   # restore archive/v0.1/ into input/
```

Restoring first saves the current `input/` to `archive/_pre-restore/` (git-ignored) so you can undo, then run `python build_content.py` to regenerate. See [`archive/README.md`](archive/README.md).

---

## Prerequisites

- **Ruby** (>= 2.7) and **Bundler** (`gem install bundler`) — `bundle install`
- **Python 3** — `build_content.py`, `backup_content.py`, and the glossary scripts (stdlib only, no pip install)

---

## Glossary generation (details)

Two glossaries are maintained in CSV and compiled to FHIR CodeSystem JSON:

| Glossary | Source CSV | Generated JSON |
|---|---|---|
| clinical | `input/ClinicalGlossary.csv` | `_resources/glossary/CodeSystem-glossary.json` |
| operational | `input/OperationalGlossary.csv` | `_resources/glossary/CodeSystem-operational-glossary.json` |

Terms are append-only — to remove one, mark it `rejected`, then physically delete it in a later cycle.

### Commands

```sh
python generate_glossary.py            # all glossaries: input CSV -> JSON
python generate_glossary.py --list     # list configured glossaries
python generate_glossary.py --to-csv   # JSON -> input CSV (re-extract; rarely needed)
```

Every run that changes a JSON writes a diff report to `glossary-changes/{glossary}-{timestamp}.md` and backs up the previous CSV/JSON.

---

## Glossary mappings (details)

`input/glossary_mappings.csv` maps model elements to glossary terms:

```
Model;ElementSuffix;GlossaryCode
StructureDefinition-be-model-vaccination.json;patient;Patient
StructureDefinition-be-model-vaccination.json;route;Route
```

`ElementSuffix` matches any element whose `id`/`path` ends with `.<suffix>`; `GlossaryCode` is a concept `code` from the glossary CodeSystem. `build_content.py` applies these automatically. To run the mapping step alone:

```sh
python add_glossary_mappings.py                                   # write element.code into the served models
python add_glossary_mappings.py --conceptmap                      # build a ConceptMap instead
python add_glossary_mappings.py --csv my.csv --output out.json    # custom paths
```

The script is idempotent (skips codes already present) and emits the glossary system `http://example.org/CodeSystem/BeSafeShareGlossary`. Keep the `Model` column in sync with the filenames in `input/models/` — rows pointing at missing files are silently skipped.

---

## Project structure

```
input/                 — ★ SOURCE OF TRUTH — everything maintainers edit
  ClinicalGlossary.csv, OperationalGlossary.csv (+ -proposed.csv)
  glossary_mappings.csv
  models/              — logical model StructureDefinition JSON (draft/ = unpublished)
archive/               — versioned snapshots of input/ (archive/v<VERSION>/)
build_content.py       — regenerate _resources/ from input/ (run after editing)
backup_content.py      — snapshot / list / restore input/ versions
generate_glossary.py   — glossary CSV <-> CodeSystem JSON
add_glossary_mappings.py — apply mappings to models / build ConceptMap
en/, fr/, nl/          — page content by language (new models appear automatically)
_config.yml            — main Jekyll config (baseurl /caresets; the Action sets each copy's own)
_config_local.yml      — local dev overrides (port 8002, empty baseurl)
_data/, _includes/, _layouts/, _sass/, assets/ — theme, templates, CSS/JS, images
_resources/glossary/   — GENERATED CodeSystem + ConceptMap JSON
_resources/models/     — GENERATED served copy of input/models/ (git-ignored)
```

### Generated / disposable (not source — safe to delete, regenerated by the scripts/build)

`_site/`, `_site.zip`, `__pycache__/`, `.jekyll-cache/`, `glossary-changes/`, `_resources/models/`, `*.backup.json`, `*.backup.csv`, and `archive/_pre-restore/`.
