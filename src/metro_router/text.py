"""Text helpers for matching what people type against station names."""

import unicodedata


def normalize(name: str) -> str:
    """Return a canonical form of ``name`` for comparisons.

    Removes accents, ignores case, treats hyphens as spaces and collapses
    repeated whitespace, so ``"  Trianon-MASP"`` and ``"trianon masp"`` match.

    Example:
        >>> normalize("Consolação")
        'consolacao'
    """
    decomposed = unicodedata.normalize("NFKD", name)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(without_accents.replace("-", " ").casefold().split())
