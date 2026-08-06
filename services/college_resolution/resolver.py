from services.college_resolution import strategies
from services.college_resolution.fuzzy import DifflibFuzzyMatcher
from services.college_resolution.sources import InMemoryAliasSource
from services.college_resolution.types import ResolutionResult


def _drop_weak_stragglers(matches, margin=0.15):
    """If the top fuzzy match clearly beats the rest, drop the weaker ones
    instead of reporting a spurious ambiguity between a strong match and a
    barely-passing one.
    """

    if len(matches) < 2:
        return matches

    top_confidence = matches[0].confidence

    return [
        match for match in matches
        if (top_confidence - match.confidence) < margin
    ]


class CollegeResolver:
    """Orchestrates the exact -> case-insensitive -> alias -> fuzzy
    strategy chain against a pluggable alias source and fuzzy matcher.

    Swap `alias_source` for a DatabaseAliasSource, or `fuzzy_matcher` for a
    RapidFuzz/pg_trgm-backed implementation, without touching this class or
    any of its callers.
    """

    def __init__(self, alias_source=None, fuzzy_matcher=None):
        self._alias_source = alias_source or InMemoryAliasSource()
        self._fuzzy_matcher = fuzzy_matcher or DifflibFuzzyMatcher()

    def resolve(self, query, limit=5):

        if not query or not query.strip():
            return ResolutionResult(query=query, matches=[])

        for strategy in (
            strategies.match_exact,
            strategies.match_case_insensitive,
            strategies.match_alias
        ):
            matches = strategy(query, self._alias_source)

            if matches:
                return ResolutionResult(query=query, matches=matches[:limit])

        fuzzy_matches = strategies.match_fuzzy(
            query,
            self._alias_source,
            self._fuzzy_matcher,
            limit
        )

        fuzzy_matches.sort(key=lambda match: match.confidence, reverse=True)
        fuzzy_matches = _drop_weak_stragglers(fuzzy_matches)

        return ResolutionResult(query=query, matches=fuzzy_matches[:limit])


_default_resolver = None


def get_default_resolver():

    global _default_resolver

    if _default_resolver is None:
        _default_resolver = CollegeResolver()

    return _default_resolver
