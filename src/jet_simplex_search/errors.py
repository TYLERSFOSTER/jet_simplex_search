"""Package-specific exceptions."""

from __future__ import annotations


class JetSimplexSearchError(Exception):
    """Base exception for `jet_simplex_search` failures."""


class InvalidGraphError(JetSimplexSearchError):
    """Raised when an input graph is structurally invalid."""


class InvalidKError(JetSimplexSearchError):
    """Raised when a requested simplex degree bound is invalid."""


class TowerAdapterError(JetSimplexSearchError):
    """Raised when a static tower adapter cannot satisfy a required query."""


class SimplexInvariantError(JetSimplexSearchError):
    """Raised when simplex or normalized graph invariants are violated."""


class ArtifactWriteError(JetSimplexSearchError):
    """Raised when a search artifact cannot be written."""

