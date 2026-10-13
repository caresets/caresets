"""
When was each served model first published, and in which release?

A StructureDefinition carries only its own `date`, the date of the version
being served. The site also wants the date of first publication. That is in
the publisher's release history: every guide lists its releases in
package-list.json, and each release's package.tgz says which logical models it
contained. The first release that contains a model is its first publication.

Writes _resources/models-publications.json:

  { "<model name>": { "guide": "core-clinical",
                      "first":  {"version": "1.1.0", "date": "2024-03-05"},
                      "latest": {"version": "1.3.0", "date": "2026-08-20"},
                      "releases": ["1.1.0", "1.2.0", "1.3.0"] } }

The viewers read it and show the first publication as a hover on the date.

Incremental: the models of a release never change once published, so each
release's model list is remembered in the output file and not downloaded
again. Packages are cached in imports/ehealth-cache/ by fetch_ehealth_models.
The CI build ("current") is not a publication and is skipped. A guide whose
history cannot be read is reported and left out; the build goes on.

  python make_publication_history.py              new releases only
  python make_publication_history.py --refresh    re-read every release
"""

import argparse
import glob
import io
import json
import os
import sys
import time

import fetch_ehealth_models as feh

ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(ROOT, "_resources", "models")
OUT = os.path.join(ROOT, "_resources", "models-publications.json")
CACHE = os.path.join(ROOT, "imports", "ehealth-cache")


def served_models():
    """{name: canonical base of its guide} for every served model."""
    out = {}
    for fn in sorted(glob.glob(os.path.join(MODELS, "**", "*.json"), recursive=True)):
        try:
            with io.open(fn, encoding="utf-8-sig") as fh:
                sd = json.load(fh)
        except (OSError, ValueError):
            continue
        if not isinstance(sd, dict) or sd.get("resourceType") != "StructureDefinition":
            continue
        url = (sd.get("url") or "").split("|")[0]
        if "/StructureDefinition/" in url:
            out[sd.get("name") or sd.get("id")] = url.split("/StructureDefinition/")[0]
    return out


def releases_of(canonical):
    """Published releases of a guide, oldest first: [{version, date, status, path}]."""
    data = json.loads(feh.fetch(canonical + "/package-list.json"))
    rels = []
    for e in data.get("list", []):
        if not e.get("version") or e.get("version") == "current" or e.get("status") == "ci-build":
            continue
        path = (e.get("path") or "").rstrip("/")
        if not path.startswith("http"):
            path = "%s/%s" % (canonical, e["version"])
        rels.append({"version": e["version"], "date": (e.get("date") or "")[:10],
                     "status": e.get("status"), "path": path})
    rels.sort(key=lambda r: r["date"] or "")
    return rels


def models_in(canonical, release):
    slug = canonical.rstrip("/").rsplit("/", 1)[-1]
    blob, _ = feh.package_bytes({"slug": slug}, release, CACHE)
    return sorted(sd.get("name") or sd.get("id") for sd in feh.logical_models(blob))


def load_out():
    if not os.path.exists(OUT):
        return {}
    with io.open(OUT, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh", action="store_true", help="re-read every release's package")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    served = served_models()
    prior = load_out()
    # what we already know, per (guide, version): the models the release held
    known = {}
    for name, info in prior.items():
        for v, ms in (info.get("_releaseModels") or {}).items():
            known[(info["guide"], v)] = ms
    out, failed = {}, []
    by_guide = {}
    for name, base in served.items():
        by_guide.setdefault(base, []).append(name)

    for base, names in sorted(by_guide.items()):
        slug = base.rstrip("/").rsplit("/", 1)[-1]
        try:
            rels = releases_of(base)
        except Exception as e:  # noqa: BLE001
            failed.append((slug, "package-list.json: %s" % e))
            print("  ! %-20s no release history (%s)" % (slug, e))
            continue
        history = {}
        for r in rels:
            key = (base, r["version"])
            if key in known and not args.refresh:
                history[r["version"]] = (r, known[key])
                continue
            try:
                ms = models_in(base, r)
            except Exception as e:  # noqa: BLE001
                print("  ! %-20s %s: package not readable (%s)" % (slug, r["version"], e))
                continue
            history[r["version"]] = (r, ms)
        print("  %-20s %d release(s)" % (slug, len(history)))
        for name in names:
            carrying = [(r, ms) for r, ms in history.values() if name in ms]
            if not carrying:
                out[name] = {"guide": slug, "first": None, "latest": None, "releases": [],
                             "_releaseModels": {v: ms for v, (r, ms) in history.items()}}
                print("     %-32s in no published release yet" % name)
                continue
            carrying.sort(key=lambda rm: rm[0]["date"] or "")
            first, latest = carrying[0][0], carrying[-1][0]
            out[name] = {
                "guide": slug,
                "first": {"version": first["version"], "date": first["date"]},
                "latest": {"version": latest["version"], "date": latest["date"]},
                "releases": [r["version"] for r, _ in carrying],
                "_releaseModels": {v: ms for v, (r, ms) in history.items()},
            }
            print("     %-32s first %s (%s)  latest %s (%s)" % (
                name, first["date"], first["version"], latest["date"], latest["version"]))

    # keep what an unreachable guide had from before, rather than dropping it
    for name, info in prior.items():
        if name not in out and name in served:
            out[name] = info
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(dict(sorted(out.items())), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("\n%d model(s) -> %s%s" % (len(out), os.path.relpath(OUT, ROOT),
                                     "" if not failed else "; %d guide(s) without history" % len(failed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
