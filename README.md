# ANZSRC 2020 → SKOS RDF

[![validate](https://github.com/leo-monus/anzsrc-for-rdf/actions/workflows/validate.yml/badge.svg)](https://github.com/leo-monus/anzsrc-for-rdf/actions/workflows/validate.yml)

Convert the ABS **ANZSRC 2020** classification spreadsheets into
[SKOS](https://www.w3.org/TR/skos-reference/) RDF vocabularies. One
vocabulary-agnostic converter handles both:

* **Fields of Research (FoR)**
* **Socio-Economic Objectives (SEO)**

Each classification is hierarchical with three levels identified by their
numeric notation (the level-3 label is "Field" for FoR and "Objective" for SEO):

| Level              | Notation | FoR      | SEO     |
|--------------------|----------|----------|---------|
| Division           | 2-digit  | 23       | 19      |
| Group              | 4-digit  | 213      | 128     |
| Field / Objective  | 6-digit  | 1967     | 840     |
| **Total concepts** |          | **2203** | **987** |

## Layout

```
anzsrc_for_to_rdf.py    # converter: XLSX -> SKOS RDF (FoR or SEO)
validate_rdf.py         # structural / SKOS integrity checks
requirements.txt        # pinned dependencies
output/                 # generated vocabulary files
  anzsrc-for_2020.rdf   # FoR, RDF/XML
  anzsrc-for_2020.ttl   # FoR, Turtle
  anzsrc-seo_2020.rdf   # SEO, RDF/XML
  anzsrc-seo_2020.ttl   # SEO, Turtle
```

The source workbooks (`*.xlsx`) are **not** tracked in this repo; point the
converter at your local copy with `--xlsx`.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Usage

The converter reads one workbook and writes one RDF file. Choose the vocabulary
by pointing `--xlsx` at the right workbook and setting `--scheme-uri`
accordingly. (The script is named `anzsrc_for_to_rdf.py` for historical reasons
but handles both vocabularies.)

| Flag           | Default                                          | Description                                        |
|----------------|--------------------------------------------------|----------------------------------------------------|
| `--xlsx`       | local FoR workbook path                          | Input `.xlsx` workbook                             |
| `--output`     | `output/anzsrc-for_2020.rdf`                     | Output file (parent dirs created automatically)    |
| `--scheme-uri` | `https://linked.data.gov.au/def/anzsrc-for/2020` | Concept scheme URI; also the concept URI namespace |
| `--format`     | `pretty-xml`                                     | rdflib format: `pretty-xml`, `xml`, `turtle`, ...  |
| `--lang`       | `en`                                             | Language tag for literals                          |
| `--issued`     | `2020-06-30`                                     | `dcterms:issued` date (empty string to omit)       |

### Fields of Research (FoR)

```bash
.venv/bin/python anzsrc_for_to_rdf.py \
    --xlsx /path/to/anzsrc-for_2020.xlsx \
    --scheme-uri https://linked.data.gov.au/def/anzsrc-for/2020 \
    --output output/anzsrc-for_2020.rdf --format pretty-xml

.venv/bin/python anzsrc_for_to_rdf.py \
    --xlsx /path/to/anzsrc-for_2020.xlsx \
    --scheme-uri https://linked.data.gov.au/def/anzsrc-for/2020 \
    --output output/anzsrc-for_2020.ttl --format turtle
```

### Socio-Economic Objectives (SEO)

```bash
.venv/bin/python anzsrc_for_to_rdf.py \
    --xlsx "/path/to/anzsrc2020_seo.xlsx" \
    --scheme-uri https://linked.data.gov.au/def/anzsrc-seo/2020 \
    --output output/anzsrc-seo_2020.rdf --format pretty-xml

.venv/bin/python anzsrc_for_to_rdf.py \
    --xlsx "/path/to/anzsrc2020_seo.xlsx" \
    --scheme-uri https://linked.data.gov.au/def/anzsrc-seo/2020 \
    --output output/anzsrc-seo_2020.ttl --format turtle
```

Run `anzsrc_for_to_rdf.py --help` for the full list of options.

## Source worksheets

* **Table 3** – master list of every concept (Divisions, Groups and
  Fields/Objectives) with its preferred label. The authoritative concept list.
* **Table 4** – definitions and exclusions for Divisions and Groups only.
* **Explanatory Notes** – free text used for the concept-scheme `skos:note`.

Tables 1 and 2 are strict subsets of Table 3 and are used only for sanity
checks.

## SKOS mapping

Concept scheme URIs (choose with `--scheme-uri`):

* FoR: `https://linked.data.gov.au/def/anzsrc-for/2020`
* SEO: `https://linked.data.gov.au/def/anzsrc-seo/2020`

Concept URIs are `{scheme-uri}/{notation}`.

Per concept:

| Property            | Source                                             |
|---------------------|----------------------------------------------------|
| `rdf:type`          | `skos:Concept`                                     |
| `skos:prefLabel`    | label (language tagged, default `en`)              |
| `skos:notation`     | the numeric code                                   |
| `skos:inScheme`     | the concept scheme                                 |
| `skos:topConceptOf` / scheme `skos:hasTopConcept` | Divisions (2-digit)  |
| `skos:broader` / `skos:narrower` | derived from the notation prefix      |
| `skos:definition`   | Table 4 *Definition* (Divisions and Groups)        |
| `skos:scopeNote`    | Table 4 *Exclusions* (Divisions and Groups)        |

Hierarchy is derived from the notation: a 4-digit Group's broader concept is
its first 2 digits; a 6-digit Field/Objective's broader concept is its first 4
digits. Definitions and exclusions exist only for Divisions and Groups because
the source spreadsheets provide them only at those levels.

## Validation

`validate_rdf.py` runs vocabulary-agnostic structural checks. Pass `--scheme-uri`
so it knows the concept namespace, plus the optional flags for stricter checks:

| Flag           | Description                                                          |
|----------------|----------------------------------------------------------------------|
| `--rdf`        | RDF file to validate (default `output/anzsrc-for_2020.rdf`)          |
| `--format`     | rdflib parse format (default `xml`; use `turtle` for `.ttl` files)   |
| `--scheme-uri` | concept scheme URI (default FoR)                                     |
| `--expect`     | optional strict counts per notation length, e.g. `2:23,4:213,6:1967` |
| `--reference`  | optional reference RDF; the notation set must match it exactly       |

FoR (strict counts + cross-check against the RDF4J export):

```bash
.venv/bin/python validate_rdf.py --rdf output/anzsrc-for_2020.rdf \
    --expect 2:23,4:213,6:1967 \
    --reference /path/to/ands-curated_anzsrc-for_2020.rdf
```

SEO (strict counts):

```bash
.venv/bin/python validate_rdf.py --rdf output/anzsrc-seo_2020.rdf \
    --scheme-uri https://linked.data.gov.au/def/anzsrc-seo/2020 \
    --expect 2:19,4:128,6:840
```

Checks performed:

* every concept has `prefLabel`, `notation` and `inScheme`;
* `hasTopConcept` / `topConceptOf` symmetry, all top concepts 2-digit;
* `broader` / `narrower` symmetry and prefix consistency;
* concept counts per notation length are reported, and enforced when `--expect` is supplied;
* the notation set matches a reference RDF exactly when `--reference` is supplied.

The script exits non-zero on any failure, so it can be wired into CI.

## Deployment

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for publishing this repo to its git remote,
the release/update workflow, and loading the vocabulary into an RDF store
(RDF4J).

## Provenance

Source: *1297.0 ANZSRC – Australian and New Zealand Standard Research
Classification, 2020* (Fields of Research and Socio-Economic Objectives),
Australian Bureau of Statistics, released 30 June 2020.
© Commonwealth of Australia 2020 · © Crown Copyright New Zealand 2020.
