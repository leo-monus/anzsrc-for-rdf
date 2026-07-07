# ANZSRC-FOR 2020 → SKOS RDF

Convert the ABS **ANZSRC 2020 Fields of Research (FoR)** spreadsheet into a
[SKOS](https://www.w3.org/TR/skos-reference/) RDF vocabulary.

The classification is hierarchical with three levels identified by their
numeric notation:

| Level    | Notation | Count |
|----------|----------|-------|
| Division | 2-digit  | 23    |
| Group    | 4-digit  | 213   |
| Field    | 6-digit  | 1967  |

Total: **2203 concepts**.

## Layout

```
anzsrc_for_to_rdf.py   # converter: XLSX -> SKOS RDF
validate_rdf.py        # structural / SKOS integrity checks
requirements.txt       # pinned dependencies
output/                # generated vocabulary files
  anzsrc-for_2020.rdf  # RDF/XML
  anzsrc-for_2020.ttl  # Turtle
```

The input workbook (`anzsrc-for_2020.xlsx`) is **not** tracked in this repo;
point the converter at your local copy with `--xlsx`.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Usage

Generate RDF/XML (default output is `output/anzsrc-for_2020.rdf`):

```bash
.venv/bin/python anzsrc_for_to_rdf.py \
    --xlsx /path/to/anzsrc-for_2020.xlsx \
    --output output/anzsrc-for_2020.rdf \
    --format pretty-xml
```

Generate Turtle as well:

```bash
.venv/bin/python anzsrc_for_to_rdf.py \
    --xlsx /path/to/anzsrc-for_2020.xlsx \
    --output output/anzsrc-for_2020.ttl \
    --format turtle
```

Run `--help` for all options (`--scheme-uri`, `--lang`, `--issued`, ...).

## Source worksheets

* **Table 3** – master list of every concept (Divisions, Groups and Fields)
  with its preferred label. This is the authoritative concept list.
* **Table 4** – definitions and exclusions for Divisions and Groups only.
* **Explanatory Notes** – free text used for the concept-scheme `skos:note`.

Tables 1 and 2 are strict subsets of Table 3 and are used only for sanity
checks.

## SKOS mapping

Concept scheme: `https://linked.data.gov.au/def/anzsrc-for/2020`
Concept URIs:   `https://linked.data.gov.au/def/anzsrc-for/2020/{notation}`

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
its first 2 digits; a 6-digit Field's broader concept is its first 4 digits.
Definitions and exclusions exist only for Divisions and Groups because the
source spreadsheet provides them only at those levels.

## Validation

```bash
.venv/bin/python validate_rdf.py --rdf output/anzsrc-for_2020.rdf \
    --reference /path/to/ands-curated_anzsrc-for_2020.rdf
```

Checks performed:

* concept counts per notation length (23 / 213 / 1967);
* every concept has `prefLabel`, `notation` and `inScheme`;
* `hasTopConcept` / `topConceptOf` symmetry, all top concepts 2-digit;
* `broader` / `narrower` symmetry and prefix consistency;
* (optional) the notation set matches a reference RDF exactly.

The script exits non-zero on any failure, so it can be wired into CI.

## Provenance

Source: *1297.0 ANZSRC – Australian and New Zealand Standard Research
Classification, 2020: Fields of Research (FoR)*, Australian Bureau of
Statistics, released 30 June 2020.
© Commonwealth of Australia 2020 · © Crown Copyright New Zealand 2020.
