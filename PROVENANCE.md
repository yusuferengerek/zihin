# Provenance

This repository is built by a script from a private archive. The archive is the system
of record. Nothing in its history was rewritten to make this tree, and no history was
carried over.

| | |
|---|---|
| Archive commit | `937b48564c31e2f9da30e1fe882ceda2613fca2f` |
| Test outcome in the READMEs | measured on a tree built from archive commit `2789cfbc962b7c999d24f0766e2d31fcb53cdec9`, the same tree file for file |
| Build script | `scripts/build_public_tree.py` in the archive, sha256 `9b63719e1c9b295231ddc70207f1a8eea16c439fda44614589c0ebc731ed1d44` |
| AppWorld package used to pack | `appworld` 0.2.0.dev0, git commit `a072b7a86e7c1d5b1d7175659d750ebb9b79f10a` |
| Derived-data manifest | `derived/MANIFEST.json`, 13 files, sha256 `4d11fa3dcd20b951d27ef51e4572e77b9410c46e8b9e4afdf03520da09217573` |

## What the archive has and this tree does not

- path docs/13-internship-report.tr.md: names the hosting institution, the workplace, the university and the advisor (K-197) (1 matched)
- path docs/13-internship-report.en.md: the English half of the same report (K-197) (1 matched)
- path vendor/appworld/appworld-0.2.0.dev0-py3-none-any.whl: AppWorld's own package, built from the pinned commit; this repository redistributes no AppWorld binaries. The fallback mirror stays in the archive and is available to reviewers on request (K-205) (1 matched)
- path vendor/appworld/appworld_agents-0.1.0.dev0-py3-none-any.whl: AppWorld's agents package; its agent prompts carry task-instruction text, from test_normal tasks among others. The fallback mirror stays in the archive and is available to reviewers on request (K-205) (1 matched)
- suffix .sqlite: record databases ship only as encrypted release assets (K-194) (0 matched)
- prefix scripts/public_templates/: the build's own inputs: rendered into the tree where needed, and the private names list must never ship (16 matched)
- path part .cache: audit and tool caches (0 matched)
- the commit's .gitignore: tracked but ignored (0 matched)

The dated records S-60, K-126, K-129, K-134, K-198 and K-199 and the pull request log
describe the AppWorld mirror as present in the repository: that holds for the archive, and
in this tree the mirror is held in the private archive, as `vendor/appworld/README.md`
describes. Current code and comments refer to `vendor/appworld/` as the mirror's fallback
location, and in this tree that directory carries only `README.md` and `PROVENANCE.json`.

## Edits made for this tree only

These change the public tree, never the archive. Each is applied by exact anchor and the
build fails if an anchor is missing. The reason for each is given beside it.

- `scripts/check_docs_parity.py`, 2 lines removed, 0 lines added. the internship report is excluded (K-197), so it is not declared bilingual in the public tree

  Removed:

  ```
      # the internship report; it is handed to two audiences and both halves are owed
      "docs/13-internship-report",
  ```
- `scripts/check_citations.py`, 4 lines removed, 0 lines added. the internship report is excluded (K-197), so the citation sweep does not read it in the public tree

  Removed:

  ```
      # The internship report opens by claiming every number is tied to a
      # measurement file. That claim is checkable only if this sweep reads it.
      "docs/13-internship-report.tr.md",
      "docs/13-internship-report.en.md",
  ```
- `vendor/appworld/README.md`, 3 lines removed, 10 lines added. the AppWorld wheels are excluded (K-205); the text names the upstream source, the pinned commit and each wheel's sha256, and says the mirror is in the archive

  Removed:

  ```
  Buradaki iki tekerlek, sabitlediğimiz AppWorld commit'inden (`a072b7a86`)
  üretilmiş kopyalardır. **Birincil kurulum yolu değiller.** Önyükleme her zaman
  önce yukarı akışa gidiyor; buraya yalnız yukarı akış reddederse düşüyor.
  ```
- `REPRODUCE.md`, 0 lines removed, 15 lines added. the AppWorld wheels are excluded (K-205); the text names the upstream source, the pinned commit and each wheel's sha256, and says the mirror is in the archive
- `REPRODUCE.tr.md`, 0 lines removed, 15 lines added. the AppWorld wheels are excluded (K-205); the text names the upstream source, the pinned commit and each wheel's sha256, and says the mirror is in the archive
- `inputs/README.md`, 1 line removed, 2 lines added. the AppWorld wheels are excluded (K-205); the line points to vendor/appworld/README.md, which says where the mirror is held

  Removed:

  ```
  hiçbir şey uyarı vermez. `vendor/appworld/` ile aynı mantık: dosya depoda durur,
  ```
- `.github/workflows/ci.yml`, 0 lines removed, 4 lines added. the public CI scans the repository's whole history with gitleaks
- `.github/workflows/ci.yml`, 0 lines removed, 4 lines added. the public tree carries the AppWorld-derived data encrypted; the tests read it after it is unpacked
- `.github/workflows/ci.yml`, 0 lines removed, 4 lines added. the sandbox job runs tests too, so it unpacks the same data first
- `.github/workflows/ci.yml`, 5 lines removed, 4 lines added. the public build's gates run in the archive, which holds the build's inputs; the public repository scans itself with the same pinned gitleaks instead

  Removed:

  ```
        - name: Public build gates
          # Every gate of the public build, run against this commit in a temporary
          # directory that is removed afterwards (K-205). It needs the AppWorld apps and
          # data installed above, and the gitleaks installed by the previous step.
          run: uv run python scripts/build_public_tree.py --check --gitleaks gitleaks
  ```
- `scripts/count_guards.py`, 0 lines removed, 4 lines added. the public CI cannot run the build's --check, so the guard declares the script as an accepted site with that reason instead of counting it as unwired
- `experiments/colab/zihin-colab.ipynb`, 1 line removed, 1 line added. the archive's notebook clones the archive by default (K-205); the public notebook clones this repository

  Removed:

  ```
      "SLUG = os.environ.get(\"ZIHIN_REPO_SLUG\", \"yusuferengerek/zihin-archive\")\n",
  ```
- `scripts/colab_publish_results.sh`, 1 line removed, 1 line added. the archive's publish script pushes to the archive by default (K-205); the public script pushes to this repository

  Removed:

  ```
  SLUG="${ZIHIN_REPO_SLUG:-yusuferengerek/zihin-archive}"
  ```
- `experiments/colab/README.md`, 1 line removed, 1 line added. the archive's Colab link opens the archive's notebook (K-205); the public link opens this repository's

  Removed:

  ```
  <https://colab.research.google.com/github/yusuferengerek/zihin-archive/blob/main/experiments/colab/zihin-colab.ipynb>
  ```
- `experiments/colab/README.md`, 1 line removed, 1 line added. the archive's Colab instructions name the archive (K-205); the public ones name this repository

  Removed:

  ```
  4. Depo: `yusuferengerek/zihin-archive`, dal: `main`.
  ```

## Files written for this tree

These files are not in the archive. They come from the build's templates. The READMEs and
`mkdocs.yml` are rendered with counts taken from this tree and from the build's
measurement.

- `.github/workflows/pages.yml`
- `README.md`
- `README.tr.md`
- `mkdocs.yml`
- `requirements-site.txt`
- `scripts/build_site.py`

## Derived data

The files listed in `derived/MANIFEST.json` are data files that carry AppWorld route
strings, (app, api) pairs from AppWorld's own API list, or task text. They are packed into
one bundle, `derived/appworld-derived.bundle`, with AppWorld's own `pack_bundle` and the
pinned package's constants, and `scripts/unpack_derived.py` restores them to their
original paths with `appworld unpack`. Code, tests and documents that mention a route
stay in plain text.

The bundle's hash changes with every build: two packs of the same input were measured to
give different sha256 values. `derived/MANIFEST.json` is the stable identity of the
derived data. Two builds of one archive commit are byte-identical in every file except the
bundle.

The build's word scans (private names, assistant names, task text) do not read the content
of a `*.bundle` file, because a word scan over ciphertext finds random matches. Every file
packed into the bundle is scanned for names and assistant names before packing, and a hit
fails the build before anything is packed.

## Third-party content

These members of vendored third-party packages carry a string the build's scans look for.
They ship unchanged, under their own license, and pass only through an allowlist keyed by
path, member and sha256.

- none

## The record databases

The record databases are not in this tree. They ship as encrypted release assets. The
`code_commit` keys inside them refer to commits of the private archive, not of this
repository. The archive is available to reviewers on request.

## Commits and syncs

Each commit of this repository names the archive commit it mirrors in a final line,
`Archive: <hash>`. A sync runs the same build script against a newer archive commit and
applies the difference to this repository as one commit, `Sync with archive <hash>`.
