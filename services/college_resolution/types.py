from dataclasses import dataclass, field
from enum import Enum

from models import College


class MatchType(Enum):

    EXACT = "exact"
    CASE_INSENSITIVE = "case_insensitive"
    ALIAS = "alias"
    FUZZY = "fuzzy"


@dataclass
class CollegeMatch:

    college: College
    match_type: MatchType
    confidence: float
    matched_on: str


@dataclass
class ResolutionResult:

    query: str
    matches: list = field(default_factory=list)

    @property
    def best(self):
        return self.matches[0] if self.matches else None

    @property
    def is_confident(self):
        return len(self.matches) == 1

    @property
    def is_ambiguous(self):
        return len(self.matches) > 1
