# Deployment

"Deployment" for this project has two parts:

1. Publishing this source repository to its git remote.
2. Loading the generated vocabulary into an RDF triplestore (e.g. RDF4J) so it
   can be served / queried.

## 1. Prerequisites

* `git`.
* Push access to the remote as the repo owner — either the GitHub CLI
  [`gh`](https://cli.github.com/) authenticated, or an SSH key registered with
  GitHub.
* Python 3.10+ with the pinned dependencies (`requirements.txt`) if you need to
  regenerate or validate the vocabulary.

## 2. Git remote

| | |
|-----------|--------------------------------------------------|
| Remote    | `origin`                                         |
| SSH URL   | `git@github.com:leo-monus/anzsrc-for-rdf.git`    |
| HTTPS URL | `https://github.com/leo-monus/anzsrc-for-rdf`    |
| Branch    | `main`                                           |

### First-time publish

The remote was created and populated with the GitHub CLI, from the repo root:

```bash
gh repo create leo-monus/anzsrc-for-rdf --public --source=. --remote=origin --push
```

Equivalent against a pre-existing empty remote repository:

```bash
git remote add origin git@github.com:leo-monus/anzsrc-for-rdf.git
git push -u origin main
```

## 3. Release / update workflow

1. Regenerate the outputs from the source workbook and validate them:

   ```bash
   .venv/bin/python anzsrc_for_to_rdf.py \
       --xlsx /path/to/anzsrc-for_2020.xlsx \
       --output output/anzsrc-for_2020.rdf --format pretty-xml
   .venv/bin/python anzsrc_for_to_rdf.py \
       --xlsx /path/to/anzsrc-for_2020.xlsx \
       --output output/anzsrc-for_2020.ttl --format turtle
   .venv/bin/python validate_rdf.py --rdf output/anzsrc-for_2020.rdf
   ```

2. Commit and push:

   ```bash
   git add -A
   git commit -m "Update ANZSRC-FOR 2020 vocabulary"
   git push
   ```

   Optionally tag the release: `git tag -a v2020.1 -m "..." && git push --tags`.

3. Or propose the change via a branch + pull request instead of pushing to
   `main` directly:

   ```bash
   git switch -c update-$(date +%Y%m%d)
   git commit -am "Update ANZSRC-FOR 2020 vocabulary"
   git push -u origin HEAD
   gh pr create --fill
   ```

## 4. Loading the vocabulary into an RDF store (RDF4J)

The concept scheme URI is `https://linked.data.gov.au/def/anzsrc-for/2020`.
Load `output/anzsrc-for_2020.rdf` into an RDF4J repository via its REST API:

```bash
curl -X POST \
  -H "Content-Type: application/rdf+xml" \
  --data-binary @output/anzsrc-for_2020.rdf \
  "http://<rdf4j-host>:8080/rdf4j-server/repositories/<repo-id>/statements"
```

* Turtle alternative: use `Content-Type: text/turtle` with
  `output/anzsrc-for_2020.ttl`.
* To publish a new version cleanly, clear the target repository (or the named
  graph/context you load into) before re-loading. Do this with care against a
  production store.

## 5. Continuous integration (optional)

Wire validation into CI so a bad export cannot be merged/released: create a
virtual environment, `pip install -r requirements.txt`, then run
`python validate_rdf.py --rdf output/anzsrc-for_2020.rdf`. The script exits
non-zero on any integrity failure.
