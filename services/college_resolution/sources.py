from typing import Protocol

from models import College


# Seed aliases for the colleges currently in the catalog. This is Phase 1
# (in-memory). When the catalog grows, swap InMemoryAliasSource for a
# DatabaseAliasSource that implements the same CollegeAliasSource interface
# below — nothing outside this module needs to change.
COLLEGE_ALIASES = {
    "iit mumbai": "IIT Bombay",
    "iitb": "IIT Bombay",

    "iitd": "IIT Delhi",

    "iit chennai": "IIT Madras",
    "iitm": "IIT Madras",

    "iitk": "IIT Kanpur",

    "iit kgp": "IIT Kharagpur",
    "iitkgp": "IIT Kharagpur",
}


class CollegeAliasSource(Protocol):
    """Interface a college name/alias data source must implement.

    InMemoryAliasSource is the only implementation today. A future
    DatabaseAliasSource (backed by a college_alias table) implements the
    same three methods so CollegeResolver never has to change.
    """

    def resolve_alias(self, normalized_query: str):
        """Exact alias lookup. Return the canonical college name, or None."""
        ...

    def iter_aliases(self):
        """Yield (alias, canonical_name) pairs, for substring matching."""
        ...

    def all_college_names(self):
        """Return every canonical college name currently in the catalog."""
        ...


class InMemoryAliasSource:

    def __init__(self, aliases=None):
        self._aliases = aliases if aliases is not None else COLLEGE_ALIASES

    def resolve_alias(self, normalized_query):
        return self._aliases.get(normalized_query)

    def iter_aliases(self):
        return self._aliases.items()

    def all_college_names(self):
        return [college.name for college in College.query.all()]
