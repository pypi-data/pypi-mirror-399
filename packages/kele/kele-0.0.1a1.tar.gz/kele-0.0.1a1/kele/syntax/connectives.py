from __future__ import annotations

from enum import StrEnum
from typing import Final


class Connective(StrEnum):
    """Logical connectives supported by the inference engine syntax layer."""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    IMPLIES = "IMPLIES"
    EQUAL = "EQUAL"


AND: Final[Connective] = Connective.AND
OR: Final[Connective] = Connective.OR
NOT: Final[Connective] = Connective.NOT
IMPLIES: Final[Connective] = Connective.IMPLIES
EQUAL: Final[Connective] = Connective.EQUAL
