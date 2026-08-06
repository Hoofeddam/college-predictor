from services.college_resolution.resolver import get_default_resolver


def resolve_college(query):
    """Best-effort resolution to a single canonical College, or None.

    Drop-in replacement for College.query.filter_by(name=...).first(). Use
    this when you just need a college and don't need to handle ambiguity.
    """

    result = find_college_candidates(query, limit=1)

    return result.best.college if result.best else None


def find_college_candidates(query, limit=5):
    """Rich resolution: ranked candidates with match type and confidence,
    plus .best / .is_confident / .is_ambiguous helpers. Use this when the
    caller needs to react to "not found" vs "ambiguous" differently (e.g.
    the AI Counselor asking the user to disambiguate).
    """

    return get_default_resolver().resolve(query, limit=limit)
