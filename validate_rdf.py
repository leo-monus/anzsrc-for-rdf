#!/usr/bin/env python3
"""Validate a generated ANZSRC-FOR SKOS RDF file.

Runs structural / SKOS integrity checks on the generated vocabulary and,
optionally, cross-checks the set of concept notations against a reference RDF
file (e.g. an export from the existing RDF4J repository).

Usage
-----
    python validate_rdf.py --rdf output/anzsrc-for_2020.rdf
    python validate_rdf.py --rdf output/anzsrc-for_2020.rdf \
        --reference /path/to/ands-curated_anzsrc-for_2020.rdf

Exit status is non-zero if any check fails, so it can be used in CI.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from rdflib import RDF, SKOS, Graph, URIRef

DEFAULT_RDF = "output/anzsrc-for_2020.rdf"
DEFAULT_SCHEME_URI = "https://linked.data.gov.au/def/anzsrc-for/2020"

# Expected number of concepts per notation length (Divisions/Groups/Fields).
EXPECTED = {2: 23, 4: 213, 6: 1967}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--rdf", default=DEFAULT_RDF, help="RDF file to validate")
    ap.add_argument("--format", default="xml", help="rdflib parse format (default: xml)")
    ap.add_argument("--scheme-uri", default=DEFAULT_SCHEME_URI, help="Concept scheme URI")
    ap.add_argument(
        "--reference",
        help="Optional reference RDF; the concept notation set must match it exactly",
    )
    args = ap.parse_args(argv)

    scheme = URIRef(args.scheme_uri)
    base = args.scheme_uri.rstrip("/") + "/"
    problems: list = []

    g = Graph()
    g.parse(args.rdf, format=args.format)
    print(f"Parsed {len(g)} triples from {args.rdf}")

    concepts = set(g.subjects(RDF.type, SKOS.Concept))
    print(f"skos:Concept count: {len(concepts)}")

    # Every concept needs a prefLabel, a notation and inScheme.
    missing_pref = [c for c in concepts if not list(g.objects(c, SKOS.prefLabel))]
    missing_notation = [c for c in concepts if not list(g.objects(c, SKOS.notation))]
    missing_scheme = [c for c in concepts if (c, SKOS.inScheme, scheme) not in g]
    print(
        f"missing prefLabel: {len(missing_pref)}; "
        f"missing notation: {len(missing_notation)}; "
        f"missing inScheme: {len(missing_scheme)}"
    )
    problems += missing_pref + missing_notation + missing_scheme

    # Concept counts by notation length.
    by_len: dict[int, int] = {}
    for c in concepts:
        code = str(c).replace(base, "")
        by_len[len(code)] = by_len.get(len(code), 0) + 1
    print("counts by notation length:", dict(sorted(by_len.items())))
    for length, expected in EXPECTED.items():
        actual = by_len.get(length, 0)
        if actual != expected:
            problems.append(f"count mismatch for {length}-digit: {actual} != {expected}")

    # Top concepts must be symmetric and all 2-digit.
    tops = set(g.objects(scheme, SKOS.hasTopConcept))
    top_of = set(g.subjects(SKOS.topConceptOf, scheme))
    print(f"hasTopConcept: {len(tops)}; topConceptOf: {len(top_of)}; symmetric: {tops == top_of}")
    if tops != top_of:
        problems.append("hasTopConcept / topConceptOf are not symmetric")
    bad_top = [str(t).replace(base, "") for t in tops if len(str(t).replace(base, "")) != 2]
    if bad_top:
        problems.append(f"non-2-digit top concepts: {bad_top}")

    # broader / narrower must be symmetric.
    asym: list = []
    for c, p in g.subject_objects(SKOS.broader):
        if (p, SKOS.narrower, c) not in g:
            asym.append((str(c), str(p)))
    for p, c in g.subject_objects(SKOS.narrower):
        if (c, SKOS.broader, p) not in g:
            asym.append((str(c), str(p)))
    print(f"broader/narrower asymmetries: {len(asym)}")
    problems += asym

    # Each non-division concept's broader must be its notation prefix.
    bad_parent: list = []
    for c in concepts:
        code = str(c).replace(base, "")
        broaders = sorted(str(b).replace(base, "") for b in g.objects(c, SKOS.broader))
        if len(code) == 2:
            if broaders:
                bad_parent.append((code, "division has broader", broaders))
        elif broaders != [code[:-2]]:
            bad_parent.append((code, "unexpected broader", broaders))
    print(f"unexpected broader links: {len(bad_parent)} {bad_parent[:5]}")
    problems += bad_parent

    print(
        f"skos:definition: {len(list(g.subject_objects(SKOS.definition)))}; "
        f"skos:scopeNote: {len(list(g.subject_objects(SKOS.scopeNote)))}"
    )

    # Optional cross-check against a reference RDF.
    if args.reference:
        ref_text = Path(args.reference).read_text()
        pattern = re.escape(base) + r"(\d+)"
        ref_codes = set(re.findall(pattern, ref_text))
        new_codes = {str(c).replace(base, "") for c in concepts}
        print(f"reference codes: {len(ref_codes)}; generated codes: {len(new_codes)}")
        only_ref = sorted(ref_codes - new_codes)
        only_new = sorted(new_codes - ref_codes)
        print(f"in reference but not generated: {only_ref[:20]}")
        print(f"in generated but not reference: {only_new[:20]}")
        if only_ref or only_new:
            problems.append("notation set differs from reference")

    print("\nVALIDATION:", "PASS" if not problems else f"FAIL ({len(problems)} issues)")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
