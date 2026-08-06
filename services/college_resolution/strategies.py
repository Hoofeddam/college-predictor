from models import db, College
from services.college_resolution.types import CollegeMatch, MatchType


def _find_by_exact_name(name):
    return College.query.filter_by(name=name).first()


def _find_by_case_insensitive_name(name):
    return College.query.filter(
        db.func.lower(College.name) == name.strip().lower()
    ).first()


def match_exact(query, alias_source):

    college = _find_by_exact_name(query.strip())

    if not college:
        return []

    return [CollegeMatch(college, MatchType.EXACT, 1.0, query)]


def match_case_insensitive(query, alias_source):

    college = _find_by_case_insensitive_name(query)

    if not college:
        return []

    return [CollegeMatch(college, MatchType.CASE_INSENSITIVE, 0.98, query)]


def match_alias(query, alias_source):
    """Resolves known aliases/abbreviations, and free text that contains a
    canonical name or alias as a substring (e.g. "IIT Chennai (IIT Madras)",
    where the user volunteers the official name alongside a colloquial one).
    """

    normalized = query.strip().lower()
    matched_colleges = {}

    canonical_name = alias_source.resolve_alias(normalized)

    if canonical_name:
        college = _find_by_case_insensitive_name(canonical_name)

        if college:
            matched_colleges[college.id] = college

    if not matched_colleges:

        for name in alias_source.all_college_names():
            if name.lower() in normalized:
                college = _find_by_exact_name(name)

                if college:
                    matched_colleges[college.id] = college

        for alias, canonical in alias_source.iter_aliases():
            if alias in normalized:
                college = _find_by_case_insensitive_name(canonical)

                if college:
                    matched_colleges[college.id] = college

    return [
        CollegeMatch(college, MatchType.ALIAS, 0.9, query)
        for college in matched_colleges.values()
    ]


def match_fuzzy(query, alias_source, fuzzy_matcher, limit):

    names = alias_source.all_college_names()
    scored = fuzzy_matcher.find_matches(query.strip(), names, limit)

    matches = []

    for name, score in scored:
        college = _find_by_exact_name(name)

        if college:
            matches.append(CollegeMatch(college, MatchType.FUZZY, score, query))

    return matches
