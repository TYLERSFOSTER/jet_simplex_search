"""Quotient-tower accelerated simplex search."""

from jet_simplex_search.api import (
    search_simplices,
    search_skeleton_simplices,
)
from jet_simplex_search.records import SimplexSearchResult
from jet_simplex_search.results import SearchResult, SearchWithHLiftsResult
from jet_simplex_search.skeleton import skeletonize_graph

__all__ = [
    "__version__",
    "SearchResult",
    "SearchWithHLiftsResult",
    "SimplexSearchResult",
    "search_simplices",
    "search_skeleton_simplices",
    "skeletonize_graph",
]

__version__ = "0.1.0"
