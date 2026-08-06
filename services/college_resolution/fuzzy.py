import difflib
from typing import Protocol


class FuzzyMatcher(Protocol):
    """Interface for the fuzzy-matching backend used as the last-resort
    resolution stage. DifflibFuzzyMatcher is the default (stdlib, no new
    dependency). It can be swapped for RapidFuzz, PostgreSQL pg_trgm, or a
    dedicated search index later by implementing this same method and
    passing it into CollegeResolver — the resolver and every caller stay
    unchanged.
    """

    def find_matches(self, query: str, candidates: list, limit: int):
        """Return up to `limit` (candidate_name, score) pairs, best first.
        score is a similarity in [0, 1].
        """
        ...


class DifflibFuzzyMatcher:

    def __init__(self, cutoff=0.6):
        self.cutoff = cutoff

    def find_matches(self, query, candidates, limit):

        close = difflib.get_close_matches(
            query,
            candidates,
            n=limit,
            cutoff=self.cutoff
        )

        return [
            (
                name,
                difflib.SequenceMatcher(None, query.lower(), name.lower()).ratio()
            )
            for name in close
        ]
