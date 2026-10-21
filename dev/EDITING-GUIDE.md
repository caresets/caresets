# Editing the CareSets site without installing anything

This guide is for people who update the glossary, the models or the pages
**from a web browser**: you download a file, change it on your computer,
and upload it again to GitHub. You need nothing installed except Excel (or
LibreOffice), and a GitHub account with write access to
[caresets/caresets](https://github.com/caresets/caresets). Ask the
maintainers for access if the **Add file** button below is missing for you.

GitHub builds the site for you after every change. You never run a script.

---

## 1. The site, and its copies

| Address | What it is | Changes when |
|---|---|---|
| <https://caresets.github.io/caresets/> | **The published site**: the current release | a release is made ([section 7](#7-publish-a-release)) |
| <https://caresets.github.io/caresets/v0.9.1/> | One release, kept exactly as it was published | never |
| <https://caresets.github.io/caresets/dev/> | **Development version**: everything accepted so far | something is saved to `main` |
| `https://caresets.github.io/caresets/branches/<name>/` | **Preview** of one proposed change | something is saved to that branch |
| <https://caresets.github.io/caresets/versions/> | **Versions**: every release with its notes, plus `/dev/` and the branch previews currently up | anything is published |

Every copy except the published one has a coloured banner at the top saying
what it is. The **footer** of every page says which copy you are on
("Release v0.9.1", "Development version", "Branch preview …"); hold the mouse
over it to see when it was built.

**`main`** is the accepted version of the source. A **branch** is a separate
line of work: a proposed change that does not touch `main` until someone
accepts it (*merges* it). Proposing your change on a branch is the safe way:
you get a preview to check, and others can review it first.

---

## 2. Change the glossary

The glossary is one Excel workbook:
**`input/Glossaire CareSets V1.xlsx`**, sheet **`Glossaire v1`**, one row per
term.

| Column | What to put |
|---|---|
| `Item` | the term, as people read it (`Business Identifier`) |
| `statut de la def` | **`Active`** to publish the term; anything else (or empty) keeps it out |
| `Synonym` | other names, if any |
| `Definition FR`, `Définition NL`, `Definition EN` | the definition, one per language |
| `Description FR`, `Description NL`, `Description EN` | the note that explains or gives examples — not part of the definition |

The other columns (`CareSets`, `Suggested Min`, `Suggested Max`, `DataType`)
are for the authors; the site does not use them.

> Renaming an `Item` renames the term's code (`Business Identifier` becomes
> `BusinessIdentifier`), and models mapped to the old code lose their link.
> Tell the maintainers when you rename a term.

### 2.1 Download the workbook

1. Open <https://github.com/caresets/caresets/blob/main/input/Glossaire%20CareSets%20V1.xlsx>.
2. Click the **download** button (the arrow pointing down, top right of the
   file view, "Download raw file").

Always download it fresh before you start: someone else may have changed it
since your last copy.

### 2.2 Edit it

Open it in Excel, change what you need, **save it as .xlsx** with the same
name. Keep the columns and the sheet names as they are.

### 2.3 Upload it

1. Open the folder <https://github.com/caresets/caresets/tree/main/input>.
2. **Add file → Upload files**, and drop your workbook in.
   **Its name must be exactly `Glossaire CareSets V1.xlsx`.** A browser often
   saves a second download as `Glossaire CareSets V1 (1).xlsx`: rename it
   back before uploading. With a different name, GitHub keeps both files and
   the build stops with "More than one workbook in input/".
3. Under **Commit changes**, write one line saying what you changed
   ("Glossary: add Specimen, fix the NL definition of Status").
4. Choose **Create a new branch for this commit and start a pull request**,
   and give the branch a short name (`glossary-specimen`). Click
   **Propose changes**.
5. On the next page, click **Create pull request**. That is your proposal.

### 2.4 Check the preview

After 2 to 5 minutes your change is at
`https://caresets.github.io/caresets/branches/<your branch name>/` (a `/` in
the branch name becomes `-`). Look at the glossary pages there in each
language.

If the change does not appear, open the **Actions** tab: a red ✗ next to
your change means the build failed, and the log says why (usually the
workbook name, or a sheet or column renamed).

To fix something, upload the workbook again **to the same branch** (on the
upload page, choose that branch in the branch menu at the top left first,
and commit directly to it). The preview rebuilds.

### 2.5 Get it accepted

Ask a colleague to review the pull request. When it is approved, click
**Merge pull request** ([section 6](#6-review-and-accept-a-change)). The
change then appears at `/dev/`, and on the published site with the next
release.

---

## 3. Change the operational glossary

The operational terms are not in the workbook: they are in
**`input/OperationalGlossary.csv`**, a text file with one term per line and
`;` between the columns
(`Term;Display;Status;Synonym;FR;EN;NL;FR Note;EN Note;NL Note`).

**Edit it in the browser, not in Excel** — Excel changes the separators and
the accents when it saves a CSV.

1. Open <https://github.com/caresets/caresets/blob/main/input/OperationalGlossary.csv>.
2. Click the **pencil** (Edit this file).
3. Change the text. Keep exactly one `;` between columns, and no `;` inside a
   definition.
4. **Commit changes…** → write what you changed → **Create a new branch …**
   → **Propose changes** → **Create pull request**.
5. Check the preview and get it accepted as in [2.4](#24-check-the-preview)
   and [2.5](#25-get-it-accepted).

Do **not** edit `input/ClinicalGlossary.csv`: it is regenerated from the
workbook on every build, so your change would be lost. Nothing under
`_resources/` is edited by hand either.

---

## 4. Change the text of a page

The pages are in `en/`, `fr/` and `nl/`, one file per page (`glossary.md`,
`terminologies.md`, …). They are plain text with light formatting (Markdown:
`**bold**`, `[link text](https://…)`, a blank line between paragraphs).

1. Open the page's file, for example
   <https://github.com/caresets/caresets/blob/main/en/terminologies.md>.
2. Click the **pencil**, edit, and use the **Preview** tab to see the result.
   Leave the block between the two `---` lines at the top alone.
3. Propose the change on a new branch as in [section 3](#3-change-the-operational-glossary), step 4.

Change all three languages if the text exists in all three.

---

## 5. Update the models from the eHealth website

The logical models are published by eHealth in its FHIR packages
(<https://www.ehealth.fgov.be/standards/fhir/>). The site does not follow
them automatically: someone fetches them when eHealth publishes new
versions, typically every few weeks. One button does it.

1. Open <https://github.com/caresets/caresets/actions/workflows/update-models.yml>.
2. Click **Run workflow** (right), keep branch `main`, leave **guides** empty
   to fetch all of them, and click the green **Run workflow**.
3. Wait 1 to 2 minutes, then click the run in the list. Its **summary** says
   one of two things:
   - **"No model has changed since the last update"** — nothing to do.
   - **"Models updated on branch `models/ehealth-<date>`"**, with:
     - the **Preview** link, ready a few minutes later;
     - a link to open the pull request ("Open it by hand: …"), unless the
       pull request was opened for you.
4. Open the pull request from that link: **Create pull request**. Its page
   lists the models that are new, updated or moved out of draft (the full
   report is in the run's **fetch** step).
5. Check the preview: the **Logical Data Models** pages, the models that
   changed, in each language.
6. When it is right, get the pull request reviewed and merged
   ([section 6](#6-review-and-accept-a-change)).

To fetch only some guides, type their names in **guides**, separated by
spaces (`core-clinical medication`).

If you have a zip of models from the publication process instead, ask a
maintainer: importing it is not available as a button.

---

## 6. Review and accept a change

All proposed changes are under **Pull requests**:
<https://github.com/caresets/caresets/pulls>.

1. Open the pull request. **Files changed** shows what changed (a workbook
   shows only as "binary file": check the preview instead).
2. Open the preview: `https://caresets.github.io/caresets/branches/<branch>/`.
3. Leave remarks under **Conversation**, or approve under **Files changed →
   Review changes → Approve**.
4. When it is right: **Merge pull request → Confirm merge**, then **Delete
   branch**. Deleting the branch also removes its preview.

The change is then in `/dev/` a few minutes later. It reaches the published
site with the next release.

If two people changed the workbook at the same time, GitHub cannot combine
the two files: merge one, then the other person downloads the new workbook,
redoes their change and uploads it again.

---

## 7. Publish a release

A release puts what is in `/dev/` on the published site, and keeps a copy of
it for good. Check <https://caresets.github.io/caresets/dev/> first: that is
exactly what will be published.

1. Open <https://github.com/caresets/caresets/releases/new>.
2. **Choose a tag** → type the new version, e.g. `v0.9.2` → **Create new
   tag**. Target: `main`. A tag starts with `v` and a number, and is never
   reused: the next release is the next number.
3. **Release title**: the same version.
4. **Describe this release**: the release notes — what changed for readers,
   in a few lines:

   ```
   Glossary: added Specimen; revised the French definition of CareSet.
   Models: Device and DeviceUseStatement added; Problem and Procedure updated to 1.4.0.

   Site: the Home link in the top menu now opens the published site.
   ```

   They appear on the Versions page as written.
5. Leave **Set as the latest release** ticked, and click **Publish release**.

After about 5 minutes:

- <https://caresets.github.io/caresets/> says "Release v0.9.2" in the footer;
- <https://caresets.github.io/caresets/v0.9.2/> exists;
- <https://caresets.github.io/caresets/versions/> lists it first, with the
  notes;
- the release on GitHub has two downloads: `caresets-site.zip` (the site as
  published here) and `riziv-inami-site.zip` (the copy for the RIZIV-INAMI
  website).

If the content of the glossary or the models changed, the maintainers also
raise the content version (the `VERSION` file) before the release.

---

## 8. When something goes wrong

| What you see | What it means | What to do |
|---|---|---|
| Your change is not in the preview after 10 minutes | The build failed, or is still waiting | **Actions** tab: a red ✗ has a log; a yellow dot is still running. GitHub's own "pages build and deployment" step is sometimes slow. |
| "More than one workbook in input/" in the log | The workbook was uploaded with another name | Delete the extra file (open it → **…** → **Delete file**) on the same branch |
| Accents look wrong in the operational glossary | The CSV went through Excel | Undo it: propose the previous version again, then edit in the browser |
| The page still shows the old text | Your browser kept the old page | Reload with **Ctrl+F5** |
| You are not sure | | Ask in the team channel before merging; nothing is published until a release |

Nothing you do on a branch can break the published site. Merging affects
`/dev/` only. Only a release changes the published site.
