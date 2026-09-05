"""Import the official JoSAA cutoff dataset (data/cutoffs.csv) into the
existing schema.

Usage:
    python scripts/import_data.py --round 1 --year 2026
    python scripts/import_data.py --round 1 --year 2026 --quotas AI

Round and year are required and deliberately not inferred or defaulted --
the source file carries neither, and guessing would present a fabricated
value as fact in a field the mobile app displays directly to users.

--quotas is optional and defaults to importing every quota present in the
file (AI, HS, OS, GO, JK, LA in the current dataset). Pass a comma-separated
subset (e.g. --quotas AI or --quotas AI,HS,OS) to restrict a run to
particular quotas; unlisted quotas are skipped and counted, not silently
dropped.

Scope:
    - Category, Quota, Exam and CounsellingRound are used as they already
      exist; no CounsellingBody, no per-exam/per-body scoping.
    - PwD category variants are imported as ordinary Category rows.
    - Quota, previously hardcoded to "AI" when the source file only covered
      IITs, is now read per row -- this file spans all 138 JoSAA
      institutes and 6 quota codes. New Quota rows (GO/JK/LA) are created
      on demand, same as any other get-or-create lookup here.
    - Exam is derived per row from the institute, not read from a column
      (the source has none). JoSAA seats institutes by two different
      admission tests: IITs and IIT (ISM) Dhanbad, plus IISc Bangalore,
      admit by JEE Advanced rank; NITs, IIITs and other GFTIs admit by JEE
      Main rank. This is JoSAA's own institute-type rule, not a guess about
      this dataset -- see classify_exam(). Confirmed against the file: the
      24 institutes it classifies as JEE Advanced are exactly the 23 IITs
      + IISc; the remaining 114 (NITs/IIITs/GFTIs) are JEE Main.
    - Rows with a "P" (Preparatory) suffix on the closing rank are skipped
      and counted -- the schema has no field to represent that admission
      standing. Separately, a small number of rows carry a malformed,
      float-formatted rank (e.g. "1032951.0") rather than a clean integer
      or P-suffixed integer; these are skipped and counted distinctly
      (skipped_malformed_rank) rather than folded into the Preparatory
      count, since they are not the same kind of exclusion.
    - The source's gender-pool distinction (Gender-Neutral vs Female-only
      supernumerary) is not modeled -- a Female-only row is imported as an
      ordinary cutoff, indistinguishable from a Gender-Neutral one, when
      one is imported at all. Female-only rows are skipped whenever a
      Gender-Neutral row exists for the same (college, branch, quota,
      category) slice, since that row already covers the slice. Where a
      Female-only row is the *only* cutoff data for a given slice, it is
      imported instead of discarded, so this doesn't create a dataset hole
      solely because pool isn't modeled yet. These are counted and
      reported separately as fallback imports.

Branch identity: each row's Academic Program Name (e.g. "Computer Science
and Engineering (4 Years, Bachelor of Technology)") is parsed into a
subject label, a duration and a degree, via parse_program_name(). Branch
identity is (college_id, branch_name, duration_years, degree_id) -- see
models.py -- because the same subject label is sometimes offered under two
different program structures at the same institute (e.g. a plain B.Tech and
a B.Tech+M.Tech dual degree), which a name-only identity can't distinguish.

Idempotency: colleges/branches are resolved through the external-ref
crosswalk tables (source, name) -> canonical row, so re-running never
creates duplicates. Cutoff rows are upserted by their natural key (branch,
exam, category, quota, round, year); an unchanged re-run updates nothing.

The whole import is one transaction: it either commits completely or rolls
back completely.
"""

import argparse
import csv
import re
import time
from collections import Counter

from app import app
from models import (
    db,
    College,
    Branch,
    Degree,
    Exam,
    Category,
    Quota,
    CounsellingRound,
    Cutoff,
    CollegeExternalRef,
    BranchExternalRef,
)

SOURCE = "josaa_cutoffs_csv"
CUTOFFS_PATH = "data/cutoffs.csv"

EXPECTED_HEADER = [
    "Institute", "Academic Program Name", "Quota", "Seat Type",
    "Gender", "Opening Rank", "Closing Rank",
]

# Pre-existing hand-seeded colleges (database/seed_colleges.py) that also
# appear in the real dataset under their official government names.
# Pre-registering these mappings makes the importer reuse those rows (and
# their hand-entered nirf_rank/fees/website) instead of creating 5
# duplicate colleges with NULL metadata alongside the good ones.
KNOWN_COLLEGE_MAPPINGS = {
    "Indian Institute of Technology Bombay": "IIT Bombay",
    "Indian Institute of Technology Delhi": "IIT Delhi",
    "Indian Institute of Technology Madras": "IIT Madras",
    "Indian Institute of Technology Kanpur": "IIT Kanpur",
    "Indian Institute of Technology Kharagpur": "IIT Kharagpur",
}

# Curated from the 17 distinct degree descriptions actually present in the
# current dataset. classify_program_type() falls back to keyword matching
# for anything not listed here, so an unrecognized future degree string
# still gets a reasonable classification instead of failing the import.
DEGREE_PROGRAM_TYPES = {
    "Bachelor of Technology": "UG",
    "Bachelor of Science": "UG",
    "Bachelor of Architecture": "UG",
    "Bachelor of Design": "UG",
    "Bachelor of Planning": "UG",
    "B. Tech / B. Tech (Hons.)": "UG",
    "Bachelor and Master of Technology (Dual Degree)": "DUAL_DEGREE",
    "B.Tech. + M.Tech./MS (Dual Degree)": "DUAL_DEGREE",
    "Bachelor of Science and MBA (Dual Degree)": "DUAL_DEGREE",
    "Bachelor of Science and Master of Science (Dual Degree)": "DUAL_DEGREE",
    "Bachelor of Technology and MBA (Dual Degree)": "DUAL_DEGREE",
    "Integrated B. Tech. and M. Tech.": "INTEGRATED",
    "Integrated B. Tech. and MBA": "INTEGRATED",
    "Integrated Bachelor of Science-Master of Science": "INTEGRATED",
    "Integrated Master of Science": "INTEGRATED",
    "Integrated Master of Technology": "INTEGRATED",
    "Integrated Masters in Technology": "INTEGRATED",
}

_DURATION_DEGREE_RE = re.compile(r"^(\d+)\s*Years?,\s*(.+)$")


def classify_exam(institute_name):
    """IITs, IIT (ISM) Dhanbad and IISc Bangalore admit by JEE Advanced
    rank; NITs, IIITs and other GFTIs admit by JEE Main rank. See the
    module docstring for why this is derived rather than read from a
    column."""
    lowered = institute_name.lower()
    if "indian institute of technology" in lowered or "indian school of mines" in lowered:
        return "JEE Advanced"
    if "indian institute of science" in lowered:
        return "JEE Advanced"
    return "JEE Main"


def split_trailing_parenthetical(raw):
    """Splits "X (Y)" into ("X", "Y") using a depth-aware scan from the
    end, so a nested parenthetical inside Y (e.g. "...(Dual Degree)") isn't
    mistaken for the closing paren of the outer group. Returns None if the
    string doesn't end with a balanced parenthetical."""
    raw = raw.strip()
    if not raw.endswith(")"):
        return None

    depth = 0
    for i in range(len(raw) - 1, -1, -1):
        char = raw[i]
        if char == ")":
            depth += 1
        elif char == "(":
            depth -= 1
            if depth == 0:
                return raw[:i].strip(), raw[i + 1:-1].strip()
    return None


def parse_program_name(raw_name):
    """"Computer Science and Engineering (4 Years, Bachelor of Technology)"
    -> ("Computer Science and Engineering", 4, "Bachelor of Technology")."""
    split = split_trailing_parenthetical(raw_name)
    if split is None:
        raise ValueError(f"Cannot parse program name (no trailing parenthetical): {raw_name!r}")

    branch_name, inner = split
    match = _DURATION_DEGREE_RE.match(inner)
    if not match:
        raise ValueError(f"Cannot parse duration/degree from {raw_name!r} (inner: {inner!r})")

    duration_years = int(match.group(1))
    degree_name = match.group(2).strip()
    return branch_name, duration_years, degree_name


def classify_program_type(degree_name):
    if degree_name in DEGREE_PROGRAM_TYPES:
        return DEGREE_PROGRAM_TYPES[degree_name]

    lowered = degree_name.lower()
    if "dual degree" in lowered:
        return "DUAL_DEGREE"
    if "integrated" in lowered:
        return "INTEGRATED"
    return "UG"


def parse_rank(raw):
    """Returns (value_or_None, reason). reason is "ok", "preparatory" (a
    "P"-suffixed rank, meaning Preparatory admission standing -- the schema
    has no field for that) or "malformed_rank" (neither a clean integer nor
    a P-suffixed one, e.g. the float-formatted "1032951.0" rows)."""
    raw = raw.strip()
    if raw.isdigit():
        return int(raw), "ok"
    if raw.endswith("P") and raw[:-1].isdigit():
        return None, "preparatory"
    return None, "malformed_rank"


def parse_cutoffs_csv(path):
    rows = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames or []

        if len(fieldnames) != len(set(fieldnames)):
            raise ValueError(f"Duplicate column(s) in header: {fieldnames!r}")
        if fieldnames != EXPECTED_HEADER:
            raise ValueError(f"Unexpected header {fieldnames!r}, expected {EXPECTED_HEADER!r}")

        for raw in reader:
            rows.append({
                "college": raw["Institute"].strip(),
                "branch": raw["Academic Program Name"].strip(),
                "quota": raw["Quota"].strip(),
                "category": raw["Seat Type"].strip(),
                "pool": raw["Gender"].strip(),
                "opening_rank": raw["Opening Rank"].strip(),
                "closing_rank": raw["Closing Rank"].strip(),
            })

    return rows


def get_or_create_college(raw_name, cache, stats):
    if raw_name in cache:
        stats["colleges_reused"] += 1
        return cache[raw_name]

    ref = CollegeExternalRef.query.filter_by(source=SOURCE, external_name=raw_name).first()
    if ref:
        stats["colleges_reused"] += 1
        cache[raw_name] = ref.college
        return ref.college

    seed_name = KNOWN_COLLEGE_MAPPINGS.get(raw_name)
    college = College.query.filter_by(name=seed_name).first() if seed_name else None

    if college is None:
        college = College(name=raw_name)
        db.session.add(college)
        db.session.flush()  # assign college.id within the open transaction
        stats["colleges_created"] += 1
    else:
        stats["colleges_reused"] += 1

    db.session.add(CollegeExternalRef(college_id=college.id, source=SOURCE, external_name=raw_name))
    cache[raw_name] = college
    return college


def get_or_create_degree(name, cache, stats):
    if name in cache:
        return cache[name]

    degree = Degree.query.filter_by(name=name).first()
    if degree is None:
        degree = Degree(name=name)
        db.session.add(degree)
        db.session.flush()
        stats["degrees_created"] += 1

    cache[name] = degree
    return degree


def get_or_create_branch(college, raw_name, branch_cache, degree_cache, stats):
    cache_key = (college.id, raw_name)
    if cache_key in branch_cache:
        stats["branches_reused"] += 1
        return branch_cache[cache_key]

    ref = (
        BranchExternalRef.query
        .filter_by(source=SOURCE, college_id=college.id, external_name=raw_name)
        .first()
    )
    if ref:
        stats["branches_reused"] += 1
        branch_cache[cache_key] = ref.branch
        return ref.branch

    branch_name, duration_years, degree_name = parse_program_name(raw_name)
    degree = get_or_create_degree(degree_name, degree_cache, stats)
    program_type = classify_program_type(degree_name)

    branch = Branch.query.filter_by(
        college_id=college.id,
        branch_name=branch_name,
        duration_years=duration_years,
        degree_id=degree.id,
    ).first()

    if branch is None:
        branch = Branch(
            college_id=college.id,
            branch_name=branch_name,
            duration_years=duration_years,
            degree_id=degree.id,
            program_type=program_type,
        )
        db.session.add(branch)
        db.session.flush()
        stats["branches_created"] += 1
    else:
        stats["branches_reused"] += 1

    db.session.add(BranchExternalRef(
        branch_id=branch.id, college_id=college.id, source=SOURCE, external_name=raw_name
    ))
    branch_cache[cache_key] = branch
    return branch


def get_or_create_category(name, cache, stats):
    if name in cache:
        return cache[name]
    category = Category.query.filter_by(name=name).first()
    if category is None:
        category = Category(name=name)
        db.session.add(category)
        db.session.flush()
        stats["categories_created"] += 1
    cache[name] = category
    return category


def get_or_create_exam(name, cache, stats):
    if name in cache:
        return cache[name]
    exam = Exam.query.filter_by(name=name).first()
    if exam is None:
        exam = Exam(name=name)
        db.session.add(exam)
        db.session.flush()
        stats["exams_created"] += 1
    cache[name] = exam
    return exam


def get_or_create_quota(name, cache, stats):
    if name in cache:
        return cache[name]
    quota = Quota.query.filter_by(name=name).first()
    if quota is None:
        quota = Quota(name=name)
        db.session.add(quota)
        db.session.flush()
        stats["quotas_created"] += 1
    cache[name] = quota
    return quota


def get_or_create_round(round_no, stats):
    round_row = CounsellingRound.query.filter_by(round_no=round_no).first()
    if round_row:
        return round_row
    round_row = CounsellingRound(round_no=round_no)
    db.session.add(round_row)
    db.session.flush()
    stats["rounds_created"] += 1
    return round_row


def upsert_cutoff(branch, exam, category, quota, round_row, year, opening_rank, closing_rank, stats, is_fallback):
    existing = Cutoff.query.filter_by(
        branch_id=branch.id,
        exam_id=exam.id,
        category_id=category.id,
        quota_id=quota.id,
        round_id=round_row.id,
        year=year,
    ).first()

    if existing is None:
        db.session.add(Cutoff(
            branch_id=branch.id,
            exam_id=exam.id,
            category_id=category.id,
            quota_id=quota.id,
            round_id=round_row.id,
            year=year,
            opening_rank=opening_rank,
            closing_rank=closing_rank,
        ))
        stats["cutoffs_created"] += 1
    elif existing.opening_rank != opening_rank or existing.closing_rank != closing_rank:
        existing.opening_rank = opening_rank
        existing.closing_rank = closing_rank
        stats["cutoffs_updated"] += 1
    else:
        stats["cutoffs_unchanged"] += 1

    # Tracked separately from created/updated/unchanged above so the
    # summary can call these out explicitly -- they're ordinary Cutoff rows
    # once imported (no pool field, no special treatment downstream), this
    # is purely a reporting marker.
    if is_fallback:
        stats["cutoffs_fallback"] += 1


def print_summary(args, stats, elapsed_seconds):
    print()
    print("=== JoSAA Import Summary ===")
    print(f"Round: {args.round}   Year: {args.year}")
    print(f"Quota filter: {args.quotas if args.quotas else '(none -- all quotas in the file)'}")
    print(f"Source file: {CUTOFFS_PATH}")
    print(f"Rows read: {stats['rows_read']}")
    if stats["rows_skipped_quota_filtered"]:
        print(f"Rows skipped (quota not in --quotas filter): {stats['rows_skipped_quota_filtered']}")
    print()
    print(f"Colleges created: {stats['colleges_created']:>5}   reused: {stats['colleges_reused']:>5}")
    print(f"Branches created: {stats['branches_created']:>5}   reused: {stats['branches_reused']:>5}")
    print(f"Degrees created: {stats['degrees_created']:>4}")
    print(f"Categories created: {stats['categories_created']:>3}")
    print(f"Exams created: {stats['exams_created']:>6}   Quotas created: {stats['quotas_created']:>3}   Rounds created: {stats['rounds_created']:>3}")
    print()
    print(f"Cutoffs created:   {stats['cutoffs_created']:>5}")
    print(f"Cutoffs updated:   {stats['cutoffs_updated']:>5}")
    print(f"Cutoffs unchanged: {stats['cutoffs_unchanged']:>5}")
    print(f"  (of which fallback imports -- Female-only row was the only")
    print(f"   cutoff data for that college/branch/quota/category): {stats['cutoffs_fallback']:>5}")
    print()
    print(f"Skipped (non-Gender-Neutral pool, Gender-Neutral row already covers the slice): {stats['skipped_pool']:>5}")
    print(f"Skipped (Preparatory / P-suffixed closing rank), total:                        {stats['skipped_preparatory']:>5}")
    print(f"  (of which unrecoverable -- fallback candidate, but rank itself")
    print(f"   is Preparatory; slice has no cutoff data at all): {stats['skipped_preparatory_unrecoverable']:>5}")
    print(f"Skipped (malformed closing rank, e.g. float-formatted), total:                 {stats['skipped_malformed_rank']:>5}")
    print(f"  (of which unrecoverable, same sense as above): {stats['skipped_malformed_rank_unrecoverable']:>5}")
    print()
    print(f"Elapsed: {elapsed_seconds:.2f}s")
    print("=== Done ===")


def _row_key(row):
    """Identifies a (college, branch, quota, category) slice -- the unit
    the Gender-Neutral-coverage / fallback-import decision is made at."""
    return (row["college"], row["branch"], row["quota"], row["category"])


def run_import(args):
    start = time.time()
    stats = Counter()

    rows = parse_cutoffs_csv(CUTOFFS_PATH)
    stats["rows_read"] = len(rows)

    quota_filter = None
    if args.quotas:
        quota_filter = {q.strip().upper() for q in args.quotas.split(",") if q.strip()}
        rows_in_scope = [row for row in rows if row["quota"].upper() in quota_filter]
        stats["rows_skipped_quota_filtered"] = len(rows) - len(rows_in_scope)
    else:
        rows_in_scope = rows

    # Which (college, branch, quota, category) slices have a Gender-Neutral
    # row at all, among rows actually in scope? Needed before deciding, row
    # by row, whether a Female-only row is a redundant duplicate (skip) or
    # the only cutoff data available for that slice (fallback-import).
    gender_neutral_keys = {
        _row_key(row) for row in rows_in_scope if row["pool"] == "Gender-Neutral"
    }

    with app.app_context():
        try:
            caches = {
                "colleges": {}, "branches": {}, "degrees": {},
                "categories": {}, "exams": {}, "quotas": {},
            }
            round_row = get_or_create_round(args.round, stats)

            for row in rows_in_scope:
                is_fallback = False

                if row["pool"] != "Gender-Neutral":
                    if _row_key(row) in gender_neutral_keys:
                        stats["skipped_pool"] += 1
                        continue
                    # Only cutoff data for this slice -- import rather
                    # than leave it with no data at all.
                    is_fallback = True

                closing_rank, reason = parse_rank(row["closing_rank"])
                if reason != "ok":
                    stats[f"skipped_{reason}"] += 1
                    if is_fallback:
                        # The only cutoff data for this slice, and it's
                        # still not importable -- this slice stays
                        # uncovered, distinct from ordinary skips where a
                        # Gender-Neutral row already covers the slice.
                        stats[f"skipped_{reason}_unrecoverable"] += 1
                    continue

                opening_rank, _ = parse_rank(row["opening_rank"])

                college = get_or_create_college(row["college"], caches["colleges"], stats)
                branch = get_or_create_branch(
                    college, row["branch"], caches["branches"], caches["degrees"], stats
                )
                category = get_or_create_category(row["category"], caches["categories"], stats)
                exam = get_or_create_exam(classify_exam(row["college"]), caches["exams"], stats)
                quota = get_or_create_quota(row["quota"], caches["quotas"], stats)

                upsert_cutoff(
                    branch, exam, category, quota, round_row, args.year,
                    opening_rank, closing_rank, stats, is_fallback
                )

            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    print_summary(args, stats, time.time() - start)


def parse_args():
    parser = argparse.ArgumentParser(description="Import the JoSAA cutoff dataset from data/cutoffs.csv")
    parser.add_argument("--round", type=int, required=True, help="Counselling round number this data represents")
    parser.add_argument("--year", type=int, required=True, help="Year this cutoff data represents")
    parser.add_argument(
        "--quotas", type=str, default=None,
        help="Comma-separated quota codes to import (e.g. AI or AI,HS,OS). Default: all quotas in the file."
    )
    return parser.parse_args()


if __name__ == "__main__":
    run_import(parse_args())
